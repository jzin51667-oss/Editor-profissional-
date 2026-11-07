#!/usr/bin/env python3
"""Adiciona elementos na tela de um vídeo vertical (1080x1920).

Elementos:
  - Legendas animadas palavra a palavra (estilo karaokê) com destaque em palavras-chave
  - Emojis que "pulam" na tela nas palavras-chave
  - Barra de progresso no topo
  - Cards/títulos por seção (gancho, "não é por isso", objetivo + contexto, erros, roteiro, CTA)
  - Efeitos sonoros de "pop" sintetizados, sincronizados com os emojis

Uso:
  python3 scripts/editar_video.py ENTRADA.mp4 SAIDA.mp4 [data/transcricao.json]

A camada gráfica é desenhada com Pillow e enviada crua (RGBA) para o ffmpeg,
que a sobrepõe ao vídeo original.
"""
import json
import math
import subprocess
import sys
import wave
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30
FONT_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FONT_XBOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

YELLOW = (255, 214, 0, 255)
GREEN = (46, 230, 120, 255)
RED = (255, 64, 64, 255)
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
PURPLE = (124, 77, 255, 255)

# ----------------------------------------------------------------- easing

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_back(t, s=1.9):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def ease_out_cubic(t):
    t = clamp(t) - 1
    return t * t * t + 1


def appear(t, start, end, fade_in=0.25, fade_out=0.2):
    """Retorna (progresso_entrada 0..1, alpha 0..1) ou None se invisível."""
    if t < start or t > end:
        return None
    pin = clamp((t - start) / fade_in)
    pout = clamp((end - t) / fade_out)
    return pin, min(pin, pout)


# ----------------------------------------------------------------- assets

@lru_cache(maxsize=256)
def font(path, size):
    return ImageFont.truetype(path, max(8, int(size)))


@lru_cache(maxsize=64)
def emoji_img(ch):
    f = ImageFont.truetype(FONT_EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), ch, font=f, embedded_color=True, anchor="mm")
    return im.crop(im.getbbox())


def with_alpha(im, a):
    if a >= 0.999:
        return im
    r, g, b, al = im.split()
    al = al.point(lambda v: int(v * a))
    return Image.merge("RGBA", (r, g, b, al))


def paste_center(canvas, im, cx, cy, scale=1.0, alpha=1.0, angle=0.0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if angle:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    im = with_alpha(im, alpha)
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


@lru_cache(maxsize=512)
def text_img(text, size, fill, stroke=10, stroke_fill=BLACK, path=FONT_BLACK, shadow=True):
    f = font(path, size)
    l, t, r, b = f.getbbox(text, stroke_width=stroke)
    pad = 20
    im = Image.new("RGBA", (r - l + pad * 2, b - t + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if shadow:
        d.text((pad - l + 6, pad - t + 8), text, font=f, fill=(0, 0, 0, 150),
               stroke_width=stroke, stroke_fill=(0, 0, 0, 150))
    d.text((pad - l, pad - t), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im


@lru_cache(maxsize=128)
def pill(text, size, bg, fg=WHITE, padx=36, pady=22, path=FONT_BLACK, emoji=None):
    """Etiqueta arredondada com texto (e emoji opcional à esquerda)."""
    f = font(path, size)
    l, t, r, b = f.getbbox(text)
    tw, th = r - l, b - t
    ew = 0
    em = None
    if emoji:
        em = emoji_img(emoji)
        em = em.resize((int(em.width * th * 1.3 / em.height), int(th * 1.3)), Image.LANCZOS)
        ew = em.width + 18
    w, h = tw + ew + padx * 2, th + pady * 2
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 12, w + 10, h + 12), radius=h // 2, fill=(0, 0, 0, 110))  # sombra
    d.rounded_rectangle((4, 4, w + 4, h + 4), radius=h // 2, fill=bg, outline=BLACK, width=5)
    x = 4 + padx
    if em is not None:
        im.alpha_composite(em, (x, 4 + (h - em.height) // 2))
        x += ew
    d.text((x - l, 4 + pady - t), text, font=f, fill=fg)
    return im


# ----------------------------------------------------------------- legendas

KEYWORDS = {
    "ruins": RED, "câmera": YELLOW, "pc": YELLOW, "gamer": YELLOW, "seguidores": YELLOW,
    "enrola,": RED, "vida": RED, "demora": RED, "realmente": YELLOW, "clicou": YELLOW,
    "motivo": YELLOW, "continuar": GREEN, "assistindo": GREEN, "duas": YELLOW, "coisas,": YELLOW,
    "objetivo": GREEN, "contexto": GREEN, "aprender": GREEN, "errado": RED, "erros": RED,
    "iniciantes": YELLOW, "erro": RED, "comum": RED, "ritmo": YELLOW, "corta": RED,
    "pausas": RED, "silêncio": RED, "edição": YELLOW, "básica": YELLOW, "crescer": GREEN,
    "importante": YELLOW, "roteiro": GREEN, "boa": GREEN, "história": YELLOW, "avançar": GREEN,
    "dicas": YELLOW, "comenta": GREEN, "vídeo": WHITE,
}


def build_groups(words, max_words=3, max_chars=18):
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        text = " ".join(x["w"] for x in cur)
        brk = (
            nxt is None
            or len(cur) >= max_words
            or len(text) + 1 + len(nxt["w"]) > max_chars
            or w["w"].endswith((",", ".", "?"))
            or nxt["s"] - w["e"] > 0.25
        )
        if brk:
            groups.append(cur)
            cur = []
    for gi, g in enumerate(groups):
        start = g[0]["s"]
        end = groups[gi + 1][0]["s"] if gi + 1 < len(groups) else g[-1]["e"] + 0.4
        groups[gi] = {"words": g, "s": start, "e": end}
    return groups


CAP_Y = 1330
CAP_SIZE = 92


def draw_captions(canvas, t, groups):
    for g in groups:
        if not (g["s"] <= t < g["e"]):
            continue
        # entrada do grupo: leve subida
        gp = ease_out_cubic((t - g["s"]) / 0.18)
        y = CAP_Y + (1 - gp) * 40
        imgs = []
        for w in g["words"]:
            txt = w["w"].upper().rstrip(",.")
            active = w["s"] <= t < max(w["e"], w["s"] + 0.12)
            spoken = t >= w["s"]
            base = KEYWORDS.get(w["w"].lower(), WHITE)
            color = YELLOW if active and base == WHITE else base
            if not spoken:
                color = (255, 255, 255, 255)
            sc = 1.0
            if active:
                sc = 1.0 + 0.18 * (1 - clamp((t - w["s"]) / 0.22)) + 0.06
            im = text_img(txt, CAP_SIZE, color, 11)
            a = 1.0 if spoken else 0.55
            imgs.append((im, sc, a))
        space = 0
        # a largura usa a escala de cada palavra, assim a palavra ativa "empurra" as vizinhas
        base_total = sum(im.width for im, _, _ in imgs)
        scale_fit = min(1.0, (W - 80) / (base_total * 1.12))
        total = sum(im.width * sc for im, sc, _ in imgs) * scale_fit
        x = (W - total) / 2
        for im, sc, a in imgs:
            wdt = im.width * sc * scale_fit
            paste_center(canvas, im, x + wdt / 2, y, sc * scale_fit, a * gp)
            x += wdt


# ----------------------------------------------------------------- emojis

# (tempo, emoji, x, y) — aparecem por ~1.1s com "pop"
EMOJIS = [
    (0.54, "👎", 860, 1130),
    (2.98, "📷", 220, 1120),
    (3.78, "🖥️", 540, 1110),
    (4.52, "👥", 860, 1120),
    (6.86, "🥱", 850, 1110),
    (8.70, "🐢", 230, 1110),
    (10.86, "👆", 850, 1120),
    (13.38, "👀", 540, 1120),
    (16.20, "🎯", 230, 1120),
    (17.00, "🧩", 850, 1120),
    (19.28, "🧠", 850, 1110),
    (22.74, "❌", 230, 1120),
    (25.78, "⏱️", 850, 1110),
    (26.86, "✂️", 230, 1110),
    (29.36, "🤫", 850, 1110),
    (32.38, "📈", 850, 1110),
    (34.34, "📝", 220, 1120),
    (35.82, "🎬", 860, 1110),
    (36.96, "🚀", 540, 1100),
    (39.16, "💬", 860, 1120),
]
EMOJI_DUR = 1.15


def draw_emojis(canvas, t):
    for (ts, ch, x, y) in EMOJIS:
        st = appear(t, ts, ts + EMOJI_DUR, 0.3, 0.2)
        if not st:
            continue
        pin, a = st
        sc = ease_out_back(pin) * 1.6
        bob = math.sin((t - ts) * 7) * 8
        ang = math.sin((t - ts) * 5) * 8
        paste_center(canvas, emoji_img(ch), x, y + bob, sc, a, ang)


# ----------------------------------------------------------------- cards/seções

def slide_x(pin, from_left=True):
    off = (1 - ease_out_back(pin, 1.4)) * (W * 0.8)
    return -off if from_left else off


def draw_hook(canvas, t):
    st = appear(t, 0.0, 1.95, 0.3, 0.2)
    if not st:
        return
    pin, a = st
    im = pill("SEUS VÍDEOS SÃO RUINS?", 62, RED, emoji="🚨")
    shake = math.sin(t * 40) * 4 if t > 0.3 else 0
    paste_center(canvas, im, W / 2 + shake, 300, ease_out_back(pin), a)


def draw_not_because(canvas, t):
    """1.9–5.3s: 'não é por causa de...' com itens riscados."""
    st = appear(t, 1.95, 5.5, 0.25, 0.25)
    if not st:
        return
    pin, a = st
    title = pill("NÃO É POR CAUSA DE:", 50, (30, 30, 30, 235))
    paste_center(canvas, title, W / 2, 250, ease_out_back(pin), a)
    items = [(2.98, "CÂMERA BOA", "📷"), (3.78, "PC GAMER", "🖥️"), (4.52, "SEGUIDORES", "👥")]
    for i, (ts, txt, em) in enumerate(items):
        s2 = appear(t, ts, 5.5, 0.25, 0.25)
        if not s2:
            continue
        p2, a2 = s2
        im = pill(txt, 48, (255, 255, 255, 240), BLACK, emoji=em).copy()
        # risco vermelho animado
        p3 = clamp((t - ts - 0.25) / 0.25)
        if p3 > 0:
            d = ImageDraw.Draw(im)
            y = im.height // 2
            d.line((20, y, 20 + (im.width - 40) * p3, y), fill=RED, width=12)
        cy = 370 + i * 115
        paste_center(canvas, im, W / 2 + slide_x(p2, i % 2 == 0), cy, 1.0, a2)


def draw_two_things(canvas, t):
    """14.4–24.3s: card '2 coisas: objetivo + contexto'."""
    st = appear(t, 14.9, 24.35, 0.3, 0.25)
    if not st:
        return
    pin, a = st
    title = pill("TODO VÍDEO PRECISA DE:", 50, PURPLE, emoji="✌️")
    paste_center(canvas, title, W / 2, 250, ease_out_back(pin), a)
    rows = [(16.20, "1. OBJETIVO", "🎯", 18.48), (17.00, "2. CONTEXTO", "🧩", 21.60)]
    for i, (ts, txt, em, hl) in enumerate(rows):
        s2 = appear(t, ts, 24.35, 0.3, 0.25)
        if not s2:
            continue
        p2, a2 = s2
        on = hl <= t < hl + 2.9
        bg = GREEN if on else (255, 255, 255, 240)
        im = pill(txt, 56, bg, BLACK, emoji=em)
        pulse = 1 + (0.06 * math.sin((t - hl) * 10) if on else 0)
        paste_center(canvas, im, W / 2 + slide_x(p2, i == 0), 380 + i * 130, pulse, a2)


def draw_errors(canvas, t):
    """24.4–32.9s: erro mais comum = ritmo + checklist de erros."""
    st = appear(t, 24.4, 32.85, 0.3, 0.25)
    if not st:
        return
    pin, a = st
    title = pill("ERRO Nº1: IGNORAR O RITMO", 50, RED, emoji="⚠️")
    paste_center(canvas, title, W / 2, 250, ease_out_back(pin), a)
    items = [(26.86, "NÃO CORTA O DESNECESSÁRIO"), (28.60, "PAUSAS DE SILÊNCIO"),
             (29.92, "ZERO EDIÇÃO BÁSICA")]
    for i, (ts, txt) in enumerate(items):
        s2 = appear(t, ts, 32.85, 0.3, 0.25)
        if not s2:
            continue
        p2, a2 = s2
        im = pill(txt, 42, (20, 20, 20, 235), WHITE, emoji="❌")
        paste_center(canvas, im, W / 2 + slide_x(p2, i % 2 == 0), 365 + i * 105, 1.0, a2)


def draw_formula(canvas, t):
    """32.9–37.6s: ROTEIRO + EDIÇÃO = 🚀"""
    st = appear(t, 33.0, 37.65, 0.3, 0.25)
    if not st:
        return
    pin, a = st
    im1 = pill("ROTEIRO", 60, GREEN, BLACK, emoji="📝")
    paste_center(canvas, im1, W / 2, 260, ease_out_back(pin), a)
    s2 = appear(t, 35.0, 37.65, 0.25, 0.25)
    if s2:
        p2, a2 = s2
        plus = text_img("+", 90, WHITE, 10)
        paste_center(canvas, plus, W / 2, 375, ease_out_back(p2), a2)
        im2 = pill("BOA EDIÇÃO", 60, YELLOW, BLACK, emoji="✂️")
        paste_center(canvas, im2, W / 2, 490, ease_out_back(clamp((t - 35.6) / 0.3)), a2)
    s3 = appear(t, 36.7, 37.65, 0.25, 0.25)
    if s3:
        p3, a3 = s3
        im3 = pill("HISTÓRIA QUE AVANÇA", 50, PURPLE, WHITE, emoji="🚀")
        paste_center(canvas, im3, W / 2, 620, ease_out_back(p3), a3)


def draw_cta(canvas, t):
    """37.6s–fim: comenta VÍDEO."""
    st = appear(t, 37.6, 99, 0.3, 0.2)
    if not st:
        return
    pin, a = st
    im = pill("QUER MAIS DICAS?", 56, (30, 30, 30, 235), WHITE, emoji="💡")
    paste_center(canvas, im, W / 2, 260, ease_out_back(pin), a)
    s2 = appear(t, 39.1, 99, 0.3, 0.2)
    if s2:
        p2, a2 = s2
        bubble = comment_bubble()
        pulse = 1 + 0.05 * math.sin((t - 39.1) * 9)
        paste_center(canvas, bubble, W / 2, 440, ease_out_back(p2) * pulse, a2)


@lru_cache(maxsize=1)
def comment_bubble():
    f = font(FONT_BLACK, 64)
    txt = 'COMENTA "VÍDEO"'
    l, t, r, b = f.getbbox(txt)
    w, h = r - l + 90, b - t + 60
    im = Image.new("RGBA", (w + 20, h + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, w + 6, h + 6), radius=40, fill=(255, 255, 255, 255), outline=BLACK, width=6)
    d.polygon([(w * 0.18, h + 3), (w * 0.12, h + 50), (w * 0.32, h + 3)], fill=(255, 255, 255, 255))
    d.line([(w * 0.18, h + 6), (w * 0.12, h + 50), (w * 0.32, h + 6)], fill=BLACK, width=6)
    d.text((6 + 45 - l, 6 + 30 - t), "COMENTA ", font=f, fill=(20, 20, 20, 255))
    cw = f.getlength('COMENTA ')
    d.text((6 + 45 - l + cw, 6 + 30 - t), '"VÍDEO"', font=f, fill=(220, 30, 60, 255))
    return im


# ----------------------------------------------------------------- barra de progresso

def draw_progress(canvas, t, dur):
    d = ImageDraw.Draw(canvas)
    p = clamp(t / dur)
    d.rectangle((0, 0, W, 14), fill=(0, 0, 0, 120))
    d.rectangle((0, 0, int(W * p), 14), fill=YELLOW)
    d.ellipse((int(W * p) - 12, -5, int(W * p) + 12, 19), fill=WHITE)


# ----------------------------------------------------------------- áudio (pops)

def make_pops(path, dur, times, sr=48000):
    out = np.zeros(int(sr * (dur + 1)), np.float32)
    n = int(sr * 0.09)
    tt = np.arange(n) / sr
    freq = 900 * np.exp(-tt * 18) + 380
    phase = 2 * np.pi * np.cumsum(freq) / sr
    pop = np.sin(phase) * np.exp(-tt * 45) * 0.55
    for ts in times:
        i = int(ts * sr)
        out[i:i + n] += pop[: len(out) - i]
    data = (np.clip(out, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())


# ----------------------------------------------------------------- main

def main():
    src, dst = sys.argv[1], sys.argv[2]
    tr = sys.argv[3] if len(sys.argv) > 3 else "data/transcricao.json"
    words = json.load(open(tr, encoding="utf-8"))
    groups = build_groups(words)
    dur = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src]).strip())

    pops_wav = dst + ".pops.wav"
    pop_times = [e[0] for e in EMOJIS] + [0.0, 1.95, 14.9, 24.4, 33.0, 35.6, 37.6, 39.1]
    make_pops(pops_wav, dur, sorted(pop_times))

    cmd = [
        "ffmpeg", "-y", "-v", "error", "-stats",
        "-i", src,
        "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", pops_wav,
        "-filter_complex",
        "[0:v][1:v]overlay=0:0:eof_action=pass:format=auto,format=yuv420p[v];"
        "[2:a]volume=0.35[p];[0:a][p]amix=inputs=2:duration=first:normalize=0[a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-r", "30",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", dst,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nframes = int(math.ceil(dur * FPS))
    for i in range(nframes):
        t = i / FPS
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_progress(canvas, t, dur)
        draw_hook(canvas, t)
        draw_not_because(canvas, t)
        draw_two_things(canvas, t)
        draw_errors(canvas, t)
        draw_formula(canvas, t)
        draw_cta(canvas, t)
        draw_emojis(canvas, t)
        draw_captions(canvas, t, groups)
        proc.stdin.write(canvas.tobytes())
    proc.stdin.close()
    proc.wait()
    if proc.returncode:
        sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
