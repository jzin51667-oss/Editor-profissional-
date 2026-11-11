#!/usr/bin/env python3
"""Gera o e-book "Vidas Impossíveis" (vidas simuladas no estilo de simulador de vida).

Uso: python3 ebook-vidas/build.py  ->  ebook-vidas/dist/Vidas-Impossiveis.pdf

Conteúdo em ebook-vidas/conteudo/: arquivos .html (páginas livres) e .txt (vidas, formato abaixo).

Formato das vidas (.txt): cabeçalho "chave: valor", uma linha "---" e o corpo:
  # FASE            divisória (INFÂNCIA, ADOLESCÊNCIA…)
  @12 texto         registro na idade 12 (linhas seguidas com a mesma idade são agrupadas)
  ! Título | texto  evento        !! Título | texto  evento ruim       + Título | texto  conquista
  ? Pergunta | opção | *opção escolhida | opção
  > texto           comentário do jogador
  $ Título | felicidade saúde inteligência aparência     barras de status
  ~ texto           passagem de tempo
  = texto           lição (aparece depois do cartão de fim de vida)
  texto             parágrafo
"""
import html
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import avatares  # noqa: E402
import icones  # noqa: E402

CONT = os.path.join(HERE, "conteudo")
DIST = os.path.join(HERE, "dist")
STAT = [("😊 Felicidade", "#22c55e"), ("❤️ Saúde", "#ef4444"), ("🧠 Inteligência", "#3b82f6"), ("✨ Aparência", "#f59e0b")]


def esc(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"_(.+?)_", r"<em>\1</em>", s)
    return s


def marker(mid):
    return f'<span style="font-size:2px;color:#f3f0fb;position:absolute">@@{mid}@@</span>'


def bars(vals):
    out = []
    for (lab, col), v in zip(STAT, vals):
        out.append(f'<div class="bar"><span>{lab}</span><div class="tr"><i style="width:{v}%;background:{col}"></i></div><span class="v">{v}%</span></div>')
    return '<div class="bars">' + "".join(out) + "</div>"


def parse_avatar(spec):
    kw = {}
    for part in spec.split():
        if "=" in part:
            k, v = part.split("=", 1)
            kw[k] = v or None
    return kw


def parse_story(text):
    head, body = text.split("\n---\n", 1)
    meta = {}
    for line in head.strip().splitlines():
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    return meta, body


def story_avatars(meta):
    base = parse_avatar(meta["avatar"])
    final = dict(base, **parse_avatar(meta.get("avatar_final", "")))
    jovem = dict(base, acessorio=parse_avatar(meta.get("avatar_jovem", "")).get("acessorio"))
    jovem.update({k: v for k, v in parse_avatar(meta.get("avatar_jovem", "")).items() if k != "acessorio"})
    idoso = dict(final, **parse_avatar(meta.get("avatar_idoso", "")))
    return base, jovem, final, idoso


def opener(meta):
    base, jovem, final, idoso = story_avatars(meta)
    tl = []
    for i, (kw, fase, lab) in enumerate([(base, "bebe", "BEBÊ"), (jovem, "jovem", "JOVEM"), (final, "adulto", "AUGE"), (idoso, "idoso", "VELHICE")]):
        if i:
            tl.append('<span class="arrow">›</span>')
        kw2 = dict(kw, fase=fase)
        if fase == "bebe":
            kw2["acessorio"] = None
        tl.append(f'<div>{avatares.avatar(size=96 if fase != "adulto" else 124, **kw2)}<small>{lab}</small></div>')
    n = meta["numero"]
    return f"""
<section class="full opener" style="--c1:{meta['cor1']};--c2:{meta['cor2']}">
 <div class="bg"></div><div class="dots"></div>{marker('V' + n)}
 <div class="num">VIDA #{n}</div><div class="bignum">{n}</div>
 <div class="ico">{icones.svg(meta['icone'], 58)}</div>
 <h1><small>TENTANDO ME TORNAR</small>{esc(meta['titulo'])}</h1>
 <div class="timeline">{''.join(tl)}</div>
 <div class="ficha">
  <div class="row"><span>NOME</span><span>{esc(meta['nome'])}</span></div>
  <div class="row"><span>NASCIMENTO</span><span>{meta['nascimento']} · {esc(meta['cidade'])}</span></div>
  <div class="row"><span>DIFICULDADE</span><span style="color:#f59e0b">{meta['dificuldade']}</span></div>
  <div class="goal"><b>OBJETIVO DA VIDA</b>{esc(meta['objetivo'])}</div>
 </div>
</section>"""


def fim_card(meta):
    _, _, final, idoso = story_avatars(meta)
    res = meta.get("resultado", "ok")
    lab = {"ok": ("ok", "✔ OBJETIVO CONCLUÍDO"), "no": ("no", "✘ OBJETIVO NÃO CONCLUÍDO"), "parcial": ("", "◐ OBJETIVO PARCIAL")}[res]
    vals = [int(x) for x in meta["stats_fim"].split()]
    ano_fim = int(meta["nascimento"]) + int(meta["morte"])
    return f"""
<div class="fim">
 <div class="hd">{avatares.avatar(size=58, fase="idoso", **idoso)}<div>
  <div class="k">FIM DA VIDA</div><div class="nm">{esc(meta['nome'])}</div>
  <div class="dt">{meta['nascimento']} – {ano_fim} · morreu aos {meta['morte']} anos · {esc(meta['causa'])}</div></div></div>
 <div class="grid">
  <div>Profissão final<b>{esc(meta['profissao'])}</b></div>
  <div>Patrimônio<b>{esc(meta['patrimonio'])}</b></div>
  <div>Família<b>{esc(meta.get('familia', '—'))}</b></div>
  <div>Fama<b>{esc(meta.get('fama', '—'))}</b></div>
 </div>
 {bars(vals)}
 <div class="res"><span class="{lab[0]}">{lab[1]}</span><span>🏅 TÍTULO: {esc(meta['titulo_final']).upper()}</span></div>
</div>"""


def render_story(meta, body):
    nasc = int(meta["nascimento"])
    out = [opener(meta), f'<div class="story">']
    licoes = []
    cur_age, cur_lines = None, []

    def flush():
        nonlocal cur_age, cur_lines
        if cur_age is not None:
            ps = "".join(f"<p>{esc(x)}</p>" for x in cur_lines)
            out.append(f'<div class="age"><div class="n"><b>{cur_age}</b><small>{nasc + int(cur_age)}</small></div><div class="t">{ps}</div></div>')
        cur_age, cur_lines = None, []

    for raw in body.strip().splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        m = re.match(r"@(\d+)\s+(.*)", line)
        if m:
            if m[1] != cur_age:
                flush()
                cur_age = m[1]
            cur_lines.append(m[2])
            continue
        flush()
        if line.startswith("# "):
            out.append(f'<div class="fase"><span>{esc(line[2:])}</span></div>')
        elif line.startswith("!! ") or line.startswith("! ") or line.startswith("+ "):
            kind, rest = ("ruim", line[3:]) if line.startswith("!! ") else (("evento", line[2:]) if line[0] == "!" else ("conquista", line[2:]))
            t, _, txt = rest.partition("|")
            icon = {"ruim": "⚠️", "evento": "📩", "conquista": "🏆"}[kind]
            out.append(f'<div class="ev {kind}"><div class="hd">{icon} {esc(t.strip()).upper()}</div><div class="bd"><p>{esc(txt.strip())}</p></div></div>')
        elif line.startswith("? "):
            parts = [p.strip() for p in line[2:].split("|")]
            opts = "".join(f'<div class="on">{esc(o[1:])}</div>' if o.startswith("*") else f"<div>{esc(o)}</div>" for o in parts[1:])
            out.append(f'<div class="ev escolha"><div class="hd">🤔 ESCOLHA</div><div class="bd"><p><b>{esc(parts[0])}</b></p><div class="opts">{opts}</div></div></div>')
        elif line.startswith("> "):
            out.append(f'<div class="nota"><span class="e">💭</span><p>{esc(line[2:])}</p></div>')
        elif line.startswith("$ "):
            t, _, v = line[2:].partition("|")
            out.append(f'<div class="statsnap"><div class="tt">📊 {esc(t.strip()).upper()}</div>{bars([int(x) for x in v.split()])}</div>')
        elif line.startswith("~ "):
            out.append(f'<div class="skip">{esc(line[2:]).upper()}</div>')
        elif line.startswith("= "):
            licoes.append(line[2:])
        else:
            out.append(f"<p>{esc(line)}</p>")
    flush()
    out.append(fim_card(meta))
    for l in licoes:
        out.append(f'<div class="licao"><b class="k">O QUE ESSA VIDA ENSINA</b>{esc(l)}</div>')
    out.append("</div>")
    return "".join(out)


def cover(stories):
    cells = []
    for meta, _ in stories[:10]:
        _, _, final, _ = story_avatars(meta)
        cells.append(f'<div>{avatares.avatar(size=88, fase="adulto", **final)}<small>{esc(meta["rotulo"])}</small></div>')
    return f"""
<section class="full cover">
 <div class="dots"></div>
 <div class="top">◆ 10 VIDAS SIMULADAS ◆ DO NASCIMENTO AO FIM ◆</div>
 <div class="t1">TENTANDO ME TORNAR…</div>
 <div class="t2">VIDAS<br><span>IMPOSSÍVEIS</span></div>
 <div class="lineup">{''.join(cells)}</div>
 <div class="sub">Histórias de vidas inteiras no estilo dos simuladores de vida: profissões, sonhos impossíveis e escolhas que mudam tudo.</div>
 <div class="badges"><span class="badge">10 VIDAS</span><span class="badge">+1 VIDA QUE VOCÊ DECIDE</span><span class="badge">FICHAS PARA JOGAR</span></div>
 <div class="foot">INSPIRADO NOS SIMULADORES DE VIDA COMO O BITLIFE</div>
</section>"""


def expand(s, toc):
    s = re.sub(r"\{\{icon:(\w+):(\d+)\}\}", lambda m: icones.svg(m[1], int(m[2])), s)
    s = re.sub(r"\{\{av:([^}]*)\}\}", lambda m: avatares.avatar(**{k: (int(v) if k == "size" else v) for k, v in (p.split("=") for p in m[1].split())}), s)
    s = re.sub(r"\{\{mark:([\w-]+)\}\}", lambda m: marker(m[1]), s)
    s = s.replace("{{toc}}", toc)
    s = re.sub(r"\{\{bars:([\d ]+)\}\}", lambda m: bars([int(x) for x in m[1].split()]), s)
    return s


def hall_html(stories):
    h = ['<table><thead><tr><th></th><th>QUEM</th><th>CHEGOU A</th><th>IDADE</th><th>OBJETIVO</th></tr></thead><tbody>']
    for meta, _ in stories:
        _, _, final, _ = story_avatars(meta)
        r = {"ok": "✔", "no": "✘", "parcial": "◐"}[meta.get("resultado", "ok")]
        h.append(f'<tr><td style="width:26pt;padding:2pt">{avatares.avatar(size=30, fase="adulto", **final)}</td><td><b>{esc(meta["nome"])}</b><br><span class="small">{esc(meta["titulo"])}</span></td>'
                 f'<td>{esc(meta["titulo_final"])}</td><td style="font:800 8pt Mono">{meta["morte"]}</td><td style="font-size:11pt;text-align:center">{r}</td></tr>')
    h.append("</tbody></table>")
    return "".join(h)


def toc_html(stories, pages):
    rows = [("INÍCIO", "Como ler este livro", "inicio")]
    for meta, _ in stories:
        rows.append((f"VIDA #{meta['numero']}", meta["titulo"], "V" + meta["numero"]))
    rows += [("BÔNUS", "Vida #11: você decide", "decide"), ("JOGUE", "Crie sua própria vida", "crie"), ("FIM", "Hall da Fama e avisos", "fim")]
    h = []
    for k, t, mid in rows:
        h.append(f'<tr><td style="font:800 6.6pt Mono;color:#ff4d2e;width:46pt">{k}</td><td style="font-weight:800">{esc(t)}</td><td style="text-align:right;font:800 8pt Mono;color:#7c3aed">{pages.get(mid, "··")}</td></tr>')
    return '<table class="toc"><tbody>' + "".join(h) + "</tbody></table>"


def load():
    items = []
    for fn in sorted(os.listdir(CONT)):
        p = os.path.join(CONT, fn)
        if fn.endswith(".txt"):
            items.append(("story", parse_story(open(p, encoding="utf-8").read())))
        elif fn.endswith(".html"):
            items.append(("html", open(p, encoding="utf-8").read()))
    return items


def assemble(pages):
    items = load()
    stories = [x for k, x in items if k == "story"]
    toc = toc_html(stories, pages)
    parts = [cover(stories)]
    for kind, x in items:
        parts.append(render_story(*x) if kind == "story" else expand(x, toc).replace("{{hall}}", hall_html(stories)))
    css = open(os.path.join(HERE, "style.css"), encoding="utf-8").read()
    return f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>Vidas Impossíveis</title><style>{css}</style></head><body>{"".join(parts)}</body></html>'


def render(doc, pdf):
    path = os.path.join(DIST, "ebook.html")
    open(path, "w", encoding="utf-8").write(doc)
    js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://{path}',{{waitUntil:'load'}});await p.evaluate(()=>document.fonts.ready);
await p.pdf({{path:'{pdf}',preferCSSPageSize:true,printBackground:true}});await b.close();}})();"""
    subprocess.run(["node", "-e", js], check=True)


def find_pages(pdf):
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.check_output(["pdfinfo", pdf]).decode())[1])
    out = {}
    for i in range(1, n + 1):
        t = subprocess.check_output(["pdftotext", "-f", str(i), "-l", str(i), pdf, "-"], stderr=subprocess.DEVNULL).decode("utf-8", "ignore")
        for m in re.finditer(r"@@([\w-]+)@@", t):
            out.setdefault(m[1], i)
    return out, n


def main():
    os.makedirs(DIST, exist_ok=True)
    pdf = os.path.join(DIST, "Vidas-Impossiveis.pdf")
    render(assemble({}), pdf)
    pages, _ = find_pages(pdf)
    render(assemble(pages), pdf)
    pages2, n = find_pages(pdf)
    if pages2 != pages:
        render(assemble(pages2), pdf)
        pages2, n = find_pages(pdf)
    print(f"OK: {pdf} — {n} páginas")
    print("  " + " ".join(f"{k}:{v}" for k, v in sorted(pages2.items(), key=lambda kv: kv[1])))


if __name__ == "__main__":
    main()
