#!/usr/bin/env python3
"""Gera as artes de divulgação do e-book (feed 1080x1350 e stories 1080x1920).

Uso: python3 ebook/divulgacao/gerar.py
Precisa de: personagem.png (recorte do personagem) e capa.png (página 1 do PDF).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import icons  # noqa: E402

FONTS = """
@font-face{font-family:Display;src:url(file:///usr/share/fonts/opentype/inter/InterDisplay-Black.otf);font-weight:900}
@font-face{font-family:Inter;src:url(file:///usr/share/fonts/opentype/inter/Inter-SemiBold.otf);font-weight:600}
@font-face{font-family:Inter;src:url(file:///usr/share/fonts/opentype/inter/Inter-ExtraBold.otf);font-weight:800}
@font-face{font-family:Mono;src:url(file:///usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-ExtraBold.ttf);font-weight:800}
"""

BASE_CSS = """
*{box-sizing:border-box;margin:0}
body{width:%(w)dpx;height:%(h)dpx;overflow:hidden;background:#06071a;font-family:Inter}
.stage{position:relative;width:100%%;height:100%%;overflow:hidden}
.bg{position:absolute;inset:0;background:
 radial-gradient(circle at 70%% 42%%,rgba(139,92,246,.55),transparent 38%%),
 radial-gradient(circle at 18%% 60%%,rgba(34,211,238,.35),transparent 35%%),
 radial-gradient(circle at 85%% 5%%,rgba(59,130,246,.45),transparent 35%%),
 linear-gradient(180deg,#0a0b24,#140a33 55%%,#05060f)}
.grid{position:absolute;left:-30%%;right:-30%%;bottom:-20px;height:%(gridh)dpx;
 background-image:linear-gradient(rgba(34,211,238,.5) 2px,transparent 2px),linear-gradient(90deg,rgba(34,211,238,.5) 2px,transparent 2px);
 background-size:70px 70px;transform:perspective(420px) rotateX(62deg);transform-origin:bottom;
 -webkit-mask-image:linear-gradient(transparent,#000 60%%)}
.stars{position:absolute;inset:0}
.tag{position:absolute;left:0;right:0;text-align:center;font:800 26px Mono;letter-spacing:.32em;color:#a5f3fc}
.h1{position:absolute;left:40px;right:40px;text-align:center;font:900 %(h1)dpx/0.95 Display;color:#fff;
 text-shadow:0 0 30px rgba(34,211,238,.6),0 6px 0 #3b1d8f}
.h1 b{font-weight:900;background:linear-gradient(180deg,#fff,#a5f3fc 40%%,#22d3ee 60%%,#8b5cf6);-webkit-background-clip:text;color:transparent;text-shadow:none;
 filter:drop-shadow(0 0 18px rgba(139,92,246,.8))}
.rays{position:absolute;width:1100px;height:1100px;
 background:conic-gradient(from 0deg,transparent 0 8deg,rgba(250,204,21,.16) 8deg 14deg,transparent 14deg 40deg,rgba(34,211,238,.15) 40deg 47deg,transparent 47deg 80deg,rgba(232,121,249,.14) 80deg 87deg,transparent 87deg 125deg,rgba(250,204,21,.16) 125deg 131deg,transparent 131deg 170deg,rgba(34,211,238,.15) 170deg 177deg,transparent 177deg 215deg,rgba(232,121,249,.14) 215deg 222deg,transparent 222deg 260deg,rgba(250,204,21,.16) 260deg 266deg,transparent 266deg 305deg,rgba(34,211,238,.15) 305deg 312deg,transparent 312deg 360deg);
 -webkit-mask-image:radial-gradient(circle,#000 15%%,transparent 65%%)}
.book{position:absolute;border-radius:10px;overflow:hidden;
 box-shadow:0 0 0 3px rgba(165,243,252,.55),0 0 60px rgba(139,92,246,.9),0 40px 80px rgba(0,0,0,.7)}
.book img{display:block;width:100%%}
.book:after{content:"";position:absolute;inset:0;background:linear-gradient(115deg,rgba(255,255,255,.22),transparent 35%%)}
.spine{position:absolute;top:0;bottom:0;left:0;width:18px;background:linear-gradient(90deg,rgba(0,0,0,.55),transparent)}
.char{position:absolute;filter:drop-shadow(0 0 26px rgba(34,211,238,.55)) drop-shadow(0 20px 30px rgba(0,0,0,.6))}
.char img{display:block;width:100%%;-webkit-mask-image:linear-gradient(#000 82%%,transparent 99%%)}
.bubble{position:absolute;background:#fff;color:#14112e;border:5px solid #0b0d1a;border-radius:30px;padding:20px 26px;
 font:800 %(bub)dpx/1.15 Inter;box-shadow:8px 8px 0 #22d3ee}
.bubble:after{content:"";position:absolute;width:34px;height:34px;background:#fff;border-right:5px solid #0b0d1a;border-bottom:5px solid #0b0d1a;
 transform:rotate(45deg)}
.bubble b{color:#7c3aed}
.panel{position:absolute;left:40px;right:40px;background:rgba(10,12,32,.86);border:2px solid #333c7a;border-radius:26px;padding:26px 30px;
 backdrop-filter:blur(6px)}
.badges{display:flex;gap:14px;justify-content:center}
.badge{flex:1;text-align:center;background:linear-gradient(160deg,#1d1f4f,#11132c);border:2px solid #3b4390;border-radius:18px;padding:14px 8px}
.badge .n{font:900 46px/1 Display;color:#22d3ee}
.badge .t{font:800 17px Mono;color:#c7cdf0;letter-spacing:.08em;margin-top:6px}
.games{text-align:center;font:800 19px Mono;letter-spacing:.14em;color:#8f97c2;margin-top:18px}
.cta{position:absolute;left:50%%;transform:translateX(-50%%);white-space:nowrap;
 background:linear-gradient(90deg,#22d3ee,#8b5cf6,#e879f9);color:#fff;font:900 %(cta)dpx Display;letter-spacing:.04em;
 padding:20px 46px;border-radius:999px;border:4px solid #fff;box-shadow:0 0 40px rgba(232,121,249,.7),0 10px 0 #3b1d8f}
.float{position:absolute}
"""


def stars(w, h, n=120, seed=3):
    import random
    r = random.Random(seed)
    return "".join(
        f'<rect x="{r.uniform(0, w):.0f}" y="{r.uniform(0, h * .7):.0f}" width="{s}" height="{s}" fill="{r.choice(["#a5f3fc", "#c4b5fd", "#fff"])}" opacity="{r.uniform(.3, .9):.2f}"/>'
        for s in [r.choice([3, 4, 6]) for _ in range(n)])


def floats(items):
    return "".join(
        f'<div class="float" style="left:{x}px;top:{y}px;transform:rotate({rot}deg)">{icons.svg(n, s, glow=5)}</div>'
        for n, x, y, s, rot in items)


def feed():
    w, h = 1080, 1350
    css = BASE_CSS % dict(w=w, h=h, gridh=420, h1=104, bub=30, cta=40)
    return f"""<html><head><style>{FONTS}{css}</style></head><body><div class="stage">
<div class="bg"></div><svg class="stars" viewBox="0 0 {w} {h}">{stars(w, h)}</svg><div class="grid"></div>
<div class="tag" style="top:46px">◆ LANÇAMENTO ◆ E-BOOK ◆</div>
<div class="h1" style="top:96px">MEU E-BOOK<br><b>CHEGOU!</b></div>
<div class="rays" style="left:180px;top:150px"></div>
{floats([("controller", 40, 330, 110, -14), ("pickaxe", 960, 300, 80, 16), ("star", 70, 560, 56, 0), ("fruit", 955, 860, 70, -8), ("ghost", 900, 470, 60, 8)])}
<div class="book" style="left:545px;top:400px;width:390px;transform:rotate(6deg)"><img src="capa.png"><div class="spine"></div></div>
<div class="char" style="left:50px;top:385px;width:450px"><img src="personagem.png"></div>
<div class="bubble" style="left:360px;top:296px;width:250px">Descobri os <b>segredos</b> dos seus jogos!</div>
<style>.bubble:after{{left:46px;bottom:-21px}}</style>
<div class="panel" style="top:1062px;padding:18px 24px">
 <div class="badges"><div class="badge"><div class="n">12</div><div class="t">FASES</div></div>
 <div class="badge"><div class="n">40</div><div class="t">MISSÕES</div></div>
 <div class="badge"><div class="n">7</div><div class="t">DIAS DE DESAFIO</div></div></div>
</div>
<div class="cta" style="top:1238px">🔗 LINK NA BIO</div>
</div></body></html>"""


def story():
    w, h = 1080, 1920
    css = BASE_CSS % dict(w=w, h=h, gridh=560, h1=120, bub=34, cta=46)
    return f"""<html><head><style>{FONTS}{css}</style></head><body><div class="stage">
<div class="bg"></div><svg class="stars" viewBox="0 0 {w} {h}">{stars(w, h, 170)}</svg><div class="grid"></div>
<div class="tag" style="top:150px">◆ LANÇAMENTO ◆ E-BOOK ◆</div>
<div class="h1" style="top:210px">MEU E-BOOK<br><b>CHEGOU!</b></div>
<div class="rays" style="left:150px;top:330px"></div>
{floats([("controller", 50, 520, 120, -14), ("pickaxe", 950, 470, 86, 16), ("star", 80, 820, 60, 0), ("fruit", 950, 1150, 76, -8), ("ghost", 920, 700, 64, 8), ("heart", 70, 1130, 56, 10)])}
<div class="book" style="left:530px;top:600px;width:430px;transform:rotate(6deg)"><img src="capa.png"><div class="spine"></div></div>
<div class="char" style="left:40px;top:600px;width:500px"><img src="personagem.png"></div>
<div class="bubble" style="left:330px;top:478px;width:280px">Descobri os <b>segredos</b> dos seus jogos!</div>
<style>.bubble:after{{left:50px;bottom:-21px}}</style>
<div class="panel" style="top:1400px">
 <div class="badges"><div class="badge"><div class="n">12</div><div class="t">FASES</div></div>
 <div class="badge"><div class="n">40</div><div class="t">MISSÕES</div></div>
 <div class="badge"><div class="n">7</div><div class="t">DIAS DE DESAFIO</div></div></div>
 <div class="games">MINECRAFT · ROBLOX · BLOX FRUITS · BITLIFE<br>GTA · AMONG US · MOBILE</div>
</div>
<div class="cta" style="top:1665px">🔗 LINK NA BIO</div>
</div></body></html>"""


def shot(html, name, w, h):
    path = os.path.join(HERE, name + ".html")
    open(path, "w", encoding="utf-8").write(html)
    js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();
const p=await b.newPage({{viewport:{{width:{w},height:{h}}},deviceScaleFactor:1}});
await p.goto('file://{path}');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
await p.screenshot({{path:'{os.path.join(HERE, name + '.png')}'}});await b.close();}})();"""
    subprocess.run(["node", "-e", js], check=True)
    os.remove(path)


if __name__ == "__main__":
    shot(feed(), "divulgacao-feed", 1080, 1350)
    shot(story(), "divulgacao-stories", 1080, 1920)
    print("OK")
