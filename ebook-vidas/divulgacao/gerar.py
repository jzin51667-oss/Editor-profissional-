#!/usr/bin/env python3
"""Artes de divulgação do e-book Vidas Impossíveis (feed 1080x1350 e stories 1080x1920)."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import avatares  # noqa: E402

PERS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "ebook", "divulgacao", "personagem.png")

CSS = """
@font-face{font-family:Display;src:url(file:///usr/share/fonts/opentype/inter/InterDisplay-Black.otf)}
@font-face{font-family:Inter;src:url(file:///usr/share/fonts/opentype/inter/Inter-ExtraBold.otf);font-weight:800}
@font-face{font-family:Mono;src:url(file:///usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-ExtraBold.ttf)}
*{box-sizing:border-box;margin:0}
body{width:%(w)dpx;height:%(h)dpx;overflow:hidden;font-family:Inter}
.st{position:relative;width:100%%;height:100%%;overflow:hidden;background:linear-gradient(170deg,#ff6a3d 0%%,#ff3d5a 45%%,#7c3aed 100%%)}
.dots{position:absolute;inset:0;opacity:.16;background-image:radial-gradient(#fff 3px,transparent 3.5px);background-size:44px 44px}
.glow{position:absolute;border-radius:50%%;background:radial-gradient(circle,rgba(253,224,71,.55),transparent 65%%)}
.tag{position:absolute;left:0;right:0;text-align:center;font:800 26px Mono;letter-spacing:.3em;color:#fff}
.h{position:absolute;left:30px;right:30px;text-align:center;color:#fff;font:900 %(hs)dpx/.92 Display;text-shadow:0 10px 0 #4c1d95}
.h span{display:block;color:#fde047;font-size:.84em}
.book{position:absolute;border-radius:14px;overflow:hidden;transform:rotate(6deg);box-shadow:0 0 0 5px #fff,0 16px 0 #4c1d95,0 40px 70px rgba(0,0,0,.45)}
.book img{display:block;width:100%%}
.char{position:absolute;filter:drop-shadow(0 18px 0 rgba(76,29,149,.55))}
.char img{display:block;width:100%%;-webkit-mask-image:linear-gradient(#000 84%%,transparent 99%%)}
.bub{position:absolute;background:#fff;color:#1d1a33;border:5px solid #1d1a33;border-radius:28px;padding:18px 24px;font:800 %(bs)dpx/1.15 Inter;box-shadow:8px 8px 0 #fde047}
.bub b{color:#ff3d5a}
.bub:after{content:"";position:absolute;left:44px;bottom:-21px;width:32px;height:32px;background:#fff;border-right:5px solid #1d1a33;border-bottom:5px solid #1d1a33;transform:rotate(45deg)}
.mini{position:absolute;background:#fff;border-radius:14px;padding:6px;box-shadow:0 8px 0 rgba(76,29,149,.55)}
.panel{position:absolute;left:40px;right:40px;display:flex;gap:14px}
.b{flex:1;background:#fff;border-radius:22px;padding:16px 8px;text-align:center;box-shadow:0 10px 0 #4c1d95}
.b .n{font:900 50px/1 Display;color:#ff3d5a}
.b .t{font:800 17px Mono;letter-spacing:.06em;color:#4c1d95;margin-top:6px}
.cta{position:absolute;left:50%%;transform:translateX(-50%%);white-space:nowrap;background:#fde047;color:#1d1a33;font:900 %(cs)dpx Display;padding:20px 48px;border-radius:999px;border:5px solid #1d1a33;box-shadow:0 10px 0 #1d1a33}
"""

MINIS = [
    dict(pele="morena", cabelo="topete", cor_cabelo="preto", roupa="#facc15", acessorio="faixa"),
    dict(pele="morena", cabelo="coque", cor_cabelo="preto", roupa="#111827", acessorio="oculos"),
    dict(pele="clara", cabelo="topete", cor_cabelo="loiro", roupa="#1e293b", acessorio="gravata"),
    dict(pele="escura", cabelo="crespo", cor_cabelo="preto", roupa="#e2e8f0", acessorio="capacete"),
    dict(pele="clara", cabelo="rabo", cor_cabelo="ruivo", roupa="#4d7c0f", acessorio="faixa"),
    dict(pele="clara", cabelo="longo", cor_cabelo="rosa", roupa="#111827", acessorio="fone"),
]


def minis(pos):
    return "".join(f'<div class="mini" style="left:{x}px;top:{y}px;transform:rotate({r}deg)">{avatares.avatar(size=s, **MINIS[i])}</div>'
                   for i, (x, y, s, r) in enumerate(pos))


def feed():
    w, h = 1080, 1350
    return f"""<html><head><style>{CSS % dict(w=w, h=h, hs=118, bs=30, cs=42)}</style></head><body><div class="st">
<div class="dots"></div><div class="glow" style="left:380px;top:300px;width:900px;height:900px"></div>
<div class="tag" style="top:44px">◆ NOVO E-BOOK ◆</div>
<div class="h" style="top:92px">VIDAS<span>IMPOSSÍVEIS</span></div>
{minis([(40, 360, 92, -10), (930, 330, 92, 9), (960, 720, 80, -6), (30, 690, 80, 7)])}
<div class="book" style="left:560px;top:380px;width:380px"><img src="capa.png"></div>
<div class="char" style="left:90px;top:470px;width:430px"><img src="{PERS}"></div>
<div class="bub" style="left:300px;top:345px;width:290px">Vivi <b>10 vidas</b> impossíveis!</div>
<div class="panel" style="top:1080px"><div class="b"><div class="n">10</div><div class="t">VIDAS</div></div><div class="b"><div class="n">9</div><div class="t">FINAIS SECRETOS</div></div><div class="b"><div class="n">80</div><div class="t">PÁGINAS</div></div></div>
<div class="cta" style="top:1222px">🔗 LINK NA BIO</div>
</div></body></html>"""


def story():
    w, h = 1080, 1920
    return f"""<html><head><style>{CSS % dict(w=w, h=h, hs=132, bs=34, cs=48)}</style></head><body><div class="st">
<div class="dots"></div><div class="glow" style="left:330px;top:520px;width:1000px;height:1000px"></div>
<div class="tag" style="top:150px">◆ NOVO E-BOOK ◆</div>
<div class="h" style="top:205px">VIDAS<span>IMPOSSÍVEIS</span></div>
{minis([(40, 560, 100, -10), (930, 520, 100, 9), (950, 1040, 90, -6), (40, 1000, 90, 7), (470, 1250, 0, 0)][:4])}
<div class="book" style="left:540px;top:600px;width:420px"><img src="capa.png"></div>
<div class="char" style="left:70px;top:720px;width:480px"><img src="{PERS}"></div>
<div class="bub" style="left:290px;top:560px;width:320px">Vivi <b>10 vidas</b> impossíveis!</div>
<div class="panel" style="top:1440px"><div class="b"><div class="n">10</div><div class="t">VIDAS</div></div><div class="b"><div class="n">9</div><div class="t">FINAIS SECRETOS</div></div><div class="b"><div class="n">80</div><div class="t">PÁGINAS</div></div></div>
<div class="cta" style="top:1640px">🔗 LINK NA BIO</div>
</div></body></html>"""


def shot(doc, name, w, h):
    path = os.path.join(HERE, name + ".html")
    open(path, "w", encoding="utf-8").write(doc)
    js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();
const p=await b.newPage({{viewport:{{width:{w},height:{h}}}}});await p.goto('file://{path}');
await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
await p.screenshot({{path:'{os.path.join(HERE, name + '.png')}'}});await b.close();}})();"""
    subprocess.run(["node", "-e", js], check=True)
    os.remove(path)


if __name__ == "__main__":
    shot(feed(), "vidas-impossiveis-feed", 1080, 1350)
    shot(story(), "vidas-impossiveis-stories", 1080, 1920)
    print("OK")
