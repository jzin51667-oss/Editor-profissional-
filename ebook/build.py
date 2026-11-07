#!/usr/bin/env python3
"""Gera o PDF do e-book "Guia dos Segredos dos Games".

Uso: python3 ebook/build.py   (gera ebook/dist/Guia-dos-Segredos-dos-Games.pdf)

Requer: Playwright + Chromium, poppler-utils (pdftotext) e as fontes Inter / JetBrains Mono.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import icons  # noqa: E402

DIST = os.path.join(HERE, "dist")
CH = os.path.join(HERE, "capitulos")

# (arquivo, abertura de fase ou None)
OPENERS = {
    "01": dict(n="01", lvl="FASE 01 · TUTORIAL", icon="chest", title="O Universo dos Segredos",
               sub="De onde vieram os easter eggs, que tipos de segredo existem e como este guia vai transformar você em um caçador de descobertas.",
               loot=["A história do primeiro easter egg", "O código mais famoso dos games", "Os 6 tipos de segredo", "Sistema de XP e níveis"],
               c1="rgba(250,204,21,.30)", c2="rgba(139,92,246,.35)"),
    "02": dict(n="02", lvl="FASE 02 · MINECRAFT", icon="pickaxe", title="Minecraft: o Mundo Infinito",
               sub="Nomes mágicos, mobs raríssimos, a origem do Creeper, mineração inteligente e o que fazer quando o Warden aparece.",
               loot=["Nomes que transformam mobs", "Raridades e como conseguir", "Mapa da mineração pós-1.18", "Como sobreviver ao Warden"],
               c1="rgba(52,211,153,.35)", c2="rgba(34,211,238,.30)"),
    "03": dict(n="03", lvl="FASE 03 · ROBLOX", icon="avatar", title="Roblox: Mil Mundos em Um",
               sub="A história escondida da plataforma, como achar segredos usando insígnias, o guia de sobrevivência de DOORS e como não cair em golpes.",
               loot=["A pré-história do Roblox", "Insígnias como mapa do tesouro", "Guia das entidades de DOORS", "Escudo anti-golpe"],
               c1="rgba(59,130,246,.45)", c2="rgba(232,121,249,.25)"),
    "04": dict(n="04", lvl="FASE 04 · BLOX FRUITS", icon="fruit", title="Blox Fruits: Rumo ao Terceiro Mar",
               sub="Como os mares funcionam, tipos de fruta, as habilidades que mudam tudo, builds e como evoluir sem desperdiçar tempo.",
               loot=["Os três mares explicados", "Natural, Elemental e Fera", "Lista de habilidades essenciais", "Builds e rotas de evolução"],
               c1="rgba(232,121,249,.40)", c2="rgba(59,130,246,.30)"),
    "05": dict(n="05", lvl="FASE 05 · BITLIFE", icon="heart", title="BitLife: o Laboratório de Vidas",
               sub="Use o simulador de vida como um laboratório: estratégias para cada fase da vida, política, prisão e desafios criativos.",
               loot=["Como o jogo pensa", "Estratégia por fase da vida", "O caminho até a presidência", "Vidas-desafio originais"],
               c1="rgba(244,63,94,.35)", c2="rgba(139,92,246,.30)"),
    "06": dict(n="06", lvl="FASE 06 · GTA", icon="car", title="GTA: Mistérios da Cidade",
               sub="O coração escondido de Liberty City, o mistério do Monte Chiliad, códigos clássicos e como jogar GTA no celular sem cair em armadilha.",
               loot=["Easter eggs de três gerações", "O mistério do Chiliad", "Códigos de San Andreas e GTA V", "GTA no celular: o que é real"],
               c1="rgba(251,146,60,.35)", c2="rgba(244,63,94,.25)"),
    "07": dict(n="07", lvl="FASE 07 · AMONG US", icon="button", title="Among Us: Ninguém é Inocente",
               sub="Mecânicas que muita gente ignora, todos os papéis especiais, o método de dedução do tripulante e o manual do impostor.",
               loot=["Mapas e conexão com Henry Stickmin", "Todos os papéis explicados", "Ferramentas de informação", "Táticas dos dois lados"],
               c1="rgba(244,63,94,.40)", c2="rgba(34,211,238,.25)"),
    "08": dict(n="08", lvl="FASE 08 · MOBILE", icon="phone", title="Segredos de Bolso",
               sub="Subway Surfers, Pokémon GO, Plants vs. Zombies, o dinossauro do Chrome, Clash Royale e outros jogos que cabem no seu celular.",
               loot=["O truque do Pikachu inicial", "Os nomes secretos das Eevees", "Recordes e manhas do Subway", "O dinossauro que não acaba"],
               c1="rgba(34,211,238,.40)", c2="rgba(250,204,21,.22)"),
    "09": dict(n="09", lvl="FASE 09 · LENDAS", icon="ghost", title="Lendas, Teorias e Verdades",
               sub="Herobrine, Polybius, o Mew debaixo do caminhão e outras histórias. Aqui cada lenda recebe um veredito: mito, real ou parcialmente real.",
               loot=["8 lendas investigadas", "Selo de veredito em cada uma", "O mistério que a comunidade resolveu", "Como nasce uma lenda"],
               c1="rgba(196,181,253,.40)", c2="rgba(30,58,138,.45)"),
    "10": dict(n="10", lvl="FASE 10 · MÉTODO", icon="magnifier", title="O Método do Explorador",
               sub="As técnicas que descobridores de segredos realmente usam, como checar um boato e a diferença entre segredo e trapaça.",
               loot=["7 técnicas de exploração", "O teste do boato", "Segredo x trapaça x golpe", "Como registrar descobertas"],
               c1="rgba(34,211,238,.45)", c2="rgba(139,92,246,.30)"),
    "11": dict(n="11", lvl="FASE 11 · DESAFIOS", icon="trophy", title="Missões e Desafios",
               sub="Desafios entre jogos, um desafio de sete dias e o seu diário de explorador para registrar tudo o que descobrir.",
               loot=["Missões extras entre jogos", "Desafio de 7 dias", "Diário do explorador", "Seu ranking pessoal"],
               c1="rgba(250,204,21,.35)", c2="rgba(232,121,249,.25)"),
    "12": dict(n="12", lvl="FASE FINAL · CHEFÃO", icon="skull", title="O Desafio Final",
               sub="O quiz do chefão com perguntas sobre tudo o que você aprendeu. Acerte e conquiste o título máximo do guia.",
               loot=["Quiz com 20 perguntas", "Gabarito comentado", "Certificado de Lenda", "Sua contagem final de XP"],
               c1="rgba(244,63,94,.35)", c2="rgba(250,204,21,.25)"),
}

TOC = [
    ("INÍCIO", "Como usar este guia", "Sistema de XP, ícones e regras do jogo", "como-usar"),
    ("FASE 01", "O Universo dos Segredos", "A história dos easter eggs e os tipos de segredo", "F01"),
    ("FASE 02", "Minecraft", "Nomes mágicos, raridades, mineração e o Warden", "F02"),
    ("FASE 03", "Roblox", "História, insígnias, DOORS e segurança", "F03"),
    ("FASE 04", "Blox Fruits", "Mares, frutas, habilidades e builds", "F04"),
    ("FASE 05", "BitLife", "Estratégias, política e vidas-desafio", "F05"),
    ("FASE 06", "GTA", "Easter eggs, mistérios e códigos", "F06"),
    ("FASE 07", "Among Us", "Papéis, ferramentas e táticas", "F07"),
    ("FASE 08", "Jogos mobile", "Subway Surfers, Pokémon GO, PvZ e mais", "F08"),
    ("FASE 09", "Lendas e teorias", "Mito, real ou parcial?", "F09"),
    ("FASE 10", "O Método do Explorador", "Como descobrir segredos de verdade", "F10"),
    ("FASE 11", "Missões e desafios", "Desafio de 7 dias e diário do explorador", "F11"),
    ("FINAL", "O Desafio Final", "Quiz do chefão e certificado", "F12"),
    ("FIM", "Game Over? Não.", "Conclusão, fontes e avisos legais", "fim"),
]


def marker(mid):
    return f'<span style="font-size:2px;color:#0a0c19;position:absolute">@@{mid}@@</span>'


def opener(o):
    return f"""
<section class="full opener" style="--c1:{o['c1']};--c2:{o['c2']}">
  <div class="bg"></div><div class="pix"></div>
  {marker('F' + o['n'])}
  <div class="num">{o['n']}</div>
  <div class="lvl">{o['lvl']}</div>
  <div class="ico">{icons.svg(o['icon'], 118, glow=6)}</div>
  <div class="ttl"><h1>{o['title']}</h1><div class="s">{o['sub']}</div></div>
  <div class="loot"><div class="lt">◆ LOOT DESTA FASE</div><ul>{''.join(f'<li>{x}</li>' for x in o['loot'])}</ul></div>
  <div class="foot"><span>GUIA DOS SEGREDOS DOS GAMES</span><span>▶ PRESS START</span></div>
</section>
<div class="fase-marker">{o['lvl']}</div>
"""


def cover():
    import random
    rnd = random.Random(7)
    stars = "".join(
        f'<rect x="{rnd.uniform(0, 148):.1f}" y="{rnd.uniform(0, 120):.1f}" width="{s}" height="{s}" fill="{c}" opacity="{rnd.uniform(.3, .9):.2f}"/>'
        for s, c in [(rnd.choice([0.5, 0.7, 1.0]), rnd.choice(["#a5f3fc", "#c4b5fd", "#fff"])) for _ in range(90)])
    floats = [("controller", 13, 104, 34, -12), ("pickaxe", 112, 100, 24, 14), ("star", 20, 140, 16, 0),
              ("fruit", 116, 136, 20, -8), ("ghost", 9, 76, 18, 6), ("heart", 124, 74, 16, 10),
              ("map", 100, 146, 13, -6), ("magnifier", 41, 151, 11, 8)]
    fl = "".join(
        f'<div class="float" style="left:{x}mm;top:{y}mm;transform:rotate({r}deg);opacity:.92">{icons.svg(n, s * 3.78, glow=4)}</div>'
        for n, x, y, s, r in floats)
    return f"""
<section class="full cover">
  <div class="bg"></div>
  <svg class="stars" viewBox="0 0 148 210" preserveAspectRatio="none">{stars}</svg>
  <div class="grid"></div>
  <div class="rays"></div>
  <div class="top">◆ EDIÇÃO 2026 ◆ PARA JOGADORES CURIOSOS ◆</div>
  <div class="title">
    <div class="t1">GUIA DOS</div>
    <div class="t2">SEGREDOS</div>
    <div class="t3">DOS GAMES</div>
  </div>
  {fl}
  <div class="chestwrap">{icons.svg('chest', 210, glow=14)}</div>
  <div class="sub">Mistérios, segredos, curiosidades, desafios e descobertas que vão transformar sua maneira de jogar.</div>
  <div class="badges"><span class="badge">12 FASES</span><span class="badge">40 MISSÕES</span><span class="badge">DESAFIO DE 7 DIAS</span></div>
  <div class="edition">MINECRAFT · ROBLOX · BLOX FRUITS · BITLIFE · GTA · AMONG US · MOBILE</div>
</section>
"""


def expand(html):
    html = re.sub(r"\{\{icon:(\w+):(\d+)\}\}", lambda m: icons.svg(m[1], int(m[2])), html)
    html = re.sub(r"\{\{iconi:(\w+):(\d+)\}\}", lambda m: icons.svg(m[1], int(m[2])).replace('class="px"', 'class="px icon-inline"'), html)
    html = re.sub(r"\{\{iconr:(\w+):(\d+)\}\}", lambda m: icons.svg(m[1], int(m[2])).replace('class="px"', 'class="px side-icon"'), html)
    html = re.sub(r"(<table[^>]*>)\s*(<tr>(?:(?!</tr>).)*?<th>.*?</tr>)", r"\1<thead>\2</thead>", html, flags=re.S)
    html = re.sub(r"\{\{mark:([\w-]+)\}\}", lambda m: marker(m[1]), html)
    return html


def toc_html(pages):
    rows = []
    for k, t, s, mid in TOC:
        pg = pages.get(mid, "··")
        rows.append(f'<div class="row"><span class="k">{k}</span><span class="ti">{t}<small>{s}</small></span><span class="pg">{pg}</span></div>')
    return '<div class="toc">' + "".join(rows) + "</div>"


def assemble(pages):
    parts = [cover()]
    for fn in sorted(os.listdir(CH)):
        if not fn.endswith(".html"):
            continue
        key = fn[:2]
        src = open(os.path.join(CH, fn), encoding="utf-8").read()
        if key in OPENERS:
            parts.append(opener(OPENERS[key]))
        parts.append(expand(src).replace("{{toc}}", toc_html(pages)))
    css = open(os.path.join(HERE, "style.css"), encoding="utf-8").read()
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Guia dos Segredos dos Games</title><style>{css}</style></head><body>{''.join(parts)}</body></html>"""


def render(html, pdf):
    path = os.path.join(DIST, "ebook.html")
    open(path, "w", encoding="utf-8").write(html)
    js = f"""
const {{chromium}} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://{path}', {{waitUntil: 'load'}});
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({{path: '{pdf}', preferCSSPageSize: true, printBackground: true, displayHeaderFooter: false}});
  await b.close();
}})();"""
    subprocess.run(["node", "-e", js], check=True)


def find_pages(pdf):
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.check_output(["pdfinfo", pdf]).decode())[1])
    out = {}
    for i in range(1, n + 1):
        txt = subprocess.check_output(["pdftotext", "-f", str(i), "-l", str(i), pdf, "-"]).decode("utf-8", "ignore")
        for m in re.finditer(r"@@([\w-]+)@@", txt):
            out.setdefault(m[1], i)
    return out, n


def main():
    os.makedirs(DIST, exist_ok=True)
    pdf = os.path.join(DIST, "Guia-dos-Segredos-dos-Games.pdf")
    render(assemble({}), pdf)
    pages, n = find_pages(pdf)
    render(assemble(pages), pdf)
    pages2, n2 = find_pages(pdf)
    if pages2 != pages:
        render(assemble(pages2), pdf)
    print(f"OK: {pdf} — {n2} páginas")
    for k, v in sorted(pages2.items(), key=lambda kv: kv[1]):
        print(f"  {k}: p.{v}")


if __name__ == "__main__":
    main()
