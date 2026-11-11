#!/usr/bin/env python3
"""Gera a página de vendas de Vidas Impossíveis (index.html único, imagens embutidas).

Uso: python3 ebook-vidas/pagina-de-vendas/gerar.py
"""
import base64
import io
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VIDAS = os.path.dirname(HERE)
sys.path.insert(0, VIDAS)
import avatares  # noqa: E402

CHECKOUT = "https://pay.hotmart.com/Q108444276V?checkoutMode=10"
IMG = os.path.join(VIDAS, "pagina-de-vendas-imagens")


def uri(name, width, q=82):
    img = Image.open(os.path.join(IMG, name))
    if img.width > width:
        img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "WEBP", quality=q, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


VIDAS_LISTA = [
    ("⚽", "O melhor jogador do mundo", "Da várzea de São Gonçalo ao prêmio de melhor do planeta."),
    ("💰", "A pessoa mais rica do mundo", "Começou vendendo brigadeiro e faliu aos 27… e depois?"),
    ("🥊", "O maior lutador do mundo", "A busca pelo cinturão sem nunca perder."),
    ("🧠", "O mentalista", "Ele não lê mentes, mas a polícia precisa dele."),
    ("🇧🇷", "O presidente do Brasil", "De representante de sala até o Palácio do Planalto."),
    ("🎭", "O maior procurado do mundo", "Ele conseguiu o que queria, e pagou caro por isso."),
    ("🧟", "Sobrevivente do apocalipse zumbi", "O vírus se espalhou em 40 dias. Ela tinha um plano."),
    ("🩺", "A médica do sertão", "Reprovada, esgotada e mesmo assim decidida."),
    ("🚀", "O astronauta brasileiro", "Uma carta respondida aos 9 anos e um destino: a Lua."),
    ("🎙️", "O maior youtuber de games", "11 visualizações no primeiro vídeo. E agora?"),
]

FAQ = [
    ("Como recebo o e-book?", "Depois que o pagamento é aprovado, a Hotmart envia o acesso para o seu e-mail. O livro é um PDF que você pode baixar e guardar."),
    ("Dá para ler no celular?", "Sim. O livro foi diagramado em formato de bolso, pensado para ler no celular."),
    ("Preciso ter o jogo para ler?", "Não. As histórias são completas e divertidas mesmo para quem nunca jogou um simulador de vida. Mas, se você joga, vai querer testar os desafios."),
    ("As histórias são reais?", "Não. São histórias de ficção, inventadas no estilo dos simuladores de vida. Nomes e acontecimentos são imaginários."),
    ("É um produto oficial do BitLife?", "Não. É uma obra independente, inspirada no gênero dos simuladores de vida, sem ligação com a desenvolvedora do jogo."),
]

MINIS = [
    dict(pele="morena", cabelo="topete", cor_cabelo="preto", roupa="#facc15", acessorio="faixa"),
    dict(pele="morena", cabelo="coque", cor_cabelo="preto", roupa="#111827", acessorio="oculos"),
    dict(pele="escura", cabelo="crespo", cor_cabelo="preto", roupa="#e2e8f0", acessorio="capacete"),
    dict(pele="clara", cabelo="longo", cor_cabelo="rosa", roupa="#111827", acessorio="fone"),
]


def main():
    capa = uri("2-capa.jpg", 760)
    pers = uri("1-personagem.png", 520, 88)
    prevs = [(uri(f, 520), t) for f, t in [
        ("3-previa-abertura-de-vida.jpg", "Abertura de cada vida"),
        ("4-previa-escolhas.jpg", "Escolhas que mudam tudo"),
        ("5-previa-fim-da-vida.jpg", "O cartão de fim da vida"),
        ("6-previa-voce-decide.jpg", "A vida em que você decide"),
    ]]
    cta = lambda t, c="": f'<a class="cta {c}" href="{CHECKOUT}">{t}<span>→</span></a>'
    vidas = "".join(f'<div class="vida"><div class="em">{e}</div><div><h3>{t}</h3><p>{d}</p></div></div>' for e, t, d in VIDAS_LISTA)
    prev = "".join(f'<figure><img src="{s}" alt="{t}"><figcaption>{t}</figcaption></figure>' for s, t in prevs)
    faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQ)
    minis = "".join(f'<div class="mini m{i}">{avatares.avatar(size=64, **m)}</div>' for i, m in enumerate(MINIS))

    html = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vidas Impossíveis · Tentando me tornar…</title>
<meta name="description" content="10 vidas inteiras no estilo simulador de vida, contadas ano a ano. + 1 vida em que você decide, com 9 finais secretos.">
<meta property="og:title" content="Vidas Impossíveis">
<meta property="og:description" content="10 vidas simuladas, do nascimento ao fim. + 1 vida em que VOCÊ decide.">
<meta name="theme-color" content="#ff3d5a">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=JetBrains+Mono:wght@800&display=swap" rel="stylesheet">
<style>
:root{{--ink:#1d1a33;--bg:#f3f0fb;--line:#e2ddf3;--o:#ff4d2e;--p:#7c3aed;--y:#fde047;--dim:#6b6890}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}html,body{{overflow-x:clip}}
body{{margin:0;background:var(--bg);color:var(--ink);font:400 17px/1.6 Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased}}
img{{max-width:100%;display:block}}
.wrap{{max-width:1080px;margin:0 auto;padding:0 22px}}
.k{{font:800 13px "JetBrains Mono",monospace;letter-spacing:.18em;color:var(--o);text-transform:uppercase}}
h1,h2,h3{{margin:0;line-height:1.05;font-weight:900;letter-spacing:-.01em}}
h2{{font-size:clamp(30px,4.6vw,46px);margin:10px 0 14px}}
h2 em{{font-style:normal;color:var(--o)}}
section{{padding:76px 0;position:relative}}
.center{{text-align:center}}.lead{{font-size:19px;max-width:720px}}.center .lead{{margin:0 auto}}
.grad{{background:linear-gradient(165deg,#ff6a3d 0%,#ff3d5a 45%,#7c3aed 100%);color:#fff;position:relative;overflow:hidden}}
.grad:before{{content:"";position:absolute;inset:0;opacity:.16;background-image:radial-gradient(#fff 2px,transparent 2.4px);background-size:30px 30px;pointer-events:none}}
.grad>*{{position:relative}}

/* hero */
.hero{{padding:44px 0 80px}}
.hero .grid{{display:grid;grid-template-columns:1.05fr .95fr;gap:30px;align-items:center}}
.pill{{display:inline-block;background:#fff;color:#ff3d5a;border-radius:999px;padding:7px 16px;font:800 12px "JetBrains Mono";letter-spacing:.14em;box-shadow:0 4px 0 #4c1d95}}
.pre{{font:800 15px "JetBrains Mono";letter-spacing:.24em;margin:22px 0 4px}}
.hero h1{{font-size:clamp(52px,8vw,96px);text-shadow:0 7px 0 #4c1d95}}
.hero h1 span{{display:block;color:var(--y);font-size:.8em}}
.hero .sub{{font-size:19px;font-weight:600;margin:22px 0 22px;max-width:540px}}
.checks{{list-style:none;padding:0;margin:0 0 30px;display:grid;gap:10px}}
.checks li{{display:flex;gap:10px;font-weight:700}}
.checks li:before{{content:"✓";flex:none;width:26px;height:26px;border-radius:8px;background:#fff;color:#ff3d5a;font:900 15px/26px Inter;text-align:center;box-shadow:0 3px 0 #4c1d95}}
.visual{{position:relative;height:560px}}
.book{{position:absolute;right:0;top:20px;width:min(370px,72%);border-radius:14px;overflow:hidden;transform:rotate(6deg);box-shadow:0 0 0 6px #fff,0 16px 0 #4c1d95,0 40px 70px rgba(0,0,0,.4);animation:f 6s ease-in-out infinite}}
@keyframes f{{0%,100%{{transform:rotate(6deg) translateY(0)}}50%{{transform:rotate(5deg) translateY(-12px)}}}}
.char{{position:absolute;left:0;bottom:0;width:min(330px,60%);filter:drop-shadow(0 16px 0 rgba(76,29,149,.5))}}
.char img{{-webkit-mask-image:linear-gradient(#000 86%,transparent)}}
.bub{{position:absolute;left:4%;top:24px;z-index:2;background:#fff;color:var(--ink);border:4px solid var(--ink);border-radius:22px;padding:14px 18px;font:800 19px/1.15 Inter;box-shadow:6px 6px 0 var(--y);max-width:220px}}
.bub b{{color:#ff3d5a}}
.bub:after{{content:"";position:absolute;left:40px;bottom:-17px;width:26px;height:26px;background:#fff;border-right:4px solid var(--ink);border-bottom:4px solid var(--ink);transform:rotate(45deg)}}
.mini{{position:absolute;background:#fff;border-radius:12px;padding:5px;box-shadow:0 6px 0 rgba(76,29,149,.5);z-index:1}}
.m0{{right:-10px;top:-10px;transform:rotate(9deg)}}.m1{{left:42%;bottom:6px;transform:rotate(-7deg)}}.m2{{right:4%;bottom:-6px;transform:rotate(6deg)}}.m3{{left:-6px;top:200px;transform:rotate(-9deg)}}

.cta{{display:inline-flex;align-items:center;justify-content:center;gap:12px;text-decoration:none;color:var(--ink);background:var(--y);font:900 20px Inter;text-transform:uppercase;letter-spacing:.01em;
 padding:19px 34px;border-radius:999px;border:4px solid var(--ink);box-shadow:0 8px 0 var(--ink);transition:transform .12s,box-shadow .12s}}
.cta span{{font-size:24px;transition:transform .12s}}
.cta:hover{{transform:translateY(-3px);box-shadow:0 11px 0 var(--ink)}}.cta:hover span{{transform:translateX(4px)}}
.cta:active{{transform:translateY(5px);box-shadow:0 3px 0 var(--ink)}}
.cta.big{{font-size:22px;padding:22px 40px}}
.safe{{display:flex;flex-wrap:wrap;gap:16px;margin-top:18px;font-size:14px;font-weight:700;opacity:.92}}
.center .safe{{justify-content:center}}

/* cards */
.card{{background:#fff;border:1px solid var(--line);border-radius:22px;padding:24px;box-shadow:0 6px 0 #d9d3ef}}
.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:-46px;position:relative;z-index:2}}
.stat{{text-align:center;padding:20px 10px}}
.stat .n{{font:900 48px/1 Inter;color:var(--o)}}
.stat .t{{font:800 13px "JetBrains Mono";letter-spacing:.08em;color:#4c1d95;margin-top:8px}}
.vidas{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:32px 0 40px}}
.vida{{display:flex;gap:16px;align-items:flex-start;background:#fff;border:1px solid var(--line);border-radius:20px;padding:18px 20px;box-shadow:0 6px 0 #d9d3ef;transition:transform .15s}}
.vida:hover{{transform:translateY(-3px)}}
.vida .em{{font-size:34px;line-height:1;flex:none;width:58px;height:58px;display:grid;place-items:center;background:var(--bg);border-radius:16px}}
.vida h3{{font-size:19px;margin:4px 0 4px}}.vida p{{margin:0;color:#4a4670;font-size:15.5px;line-height:1.45}}
.feat{{display:grid;grid-template-columns:1fr 1fr;gap:12px 24px;list-style:none;padding:0;margin:26px 0 34px}}
.feat li{{display:flex;gap:12px;font-weight:700;background:#fff;border-radius:16px;padding:14px 16px;border:1px solid var(--line)}}
.feat li i{{font-style:normal;font-size:22px}}
.prev{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}}
.prev figure{{margin:0}}.prev img{{border-radius:12px;border:4px solid #fff;box-shadow:0 8px 0 #cfc7ea,0 20px 40px rgba(76,29,149,.18)}}
.prev figcaption{{text-align:center;font-weight:800;font-size:14px;margin-top:12px;color:#4a4670}}
.bonus .wrap{{display:grid;grid-template-columns:auto 1fr;gap:40px;align-items:center}}
.dice{{font-size:130px;line-height:1;filter:drop-shadow(0 10px 0 #4c1d95)}}
.bonus p{{font-size:19px;font-weight:600;max-width:640px}}
.three{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:30px}}
.three .card h3{{font-size:20px;margin:10px 0 6px}}.three .card p{{margin:0;color:#4a4670}}.three .e{{font-size:36px}}
.offer{{max-width:620px;margin:0 auto;background:#fff;border:3px solid var(--o);border-radius:28px;padding:34px 30px;text-align:center;box-shadow:0 12px 0 #4c1d95}}
.offer img{{width:150px;margin:0 auto 18px;border-radius:10px;transform:rotate(-4deg);box-shadow:0 8px 0 #4c1d95}}
.offer ul{{text-align:left;list-style:none;padding:0;margin:20px 0 28px;display:grid;gap:9px}}
.offer li{{display:flex;gap:10px;font-weight:700}}.offer li:before{{content:"◆";color:var(--o)}}
.offer .safe{{color:#4a4670;justify-content:center}}
.faq{{max-width:760px;margin:28px auto 0;display:grid;gap:12px}}
details{{background:#fff;border:1px solid var(--line);border-radius:16px;padding:18px 22px;box-shadow:0 4px 0 #d9d3ef}}
summary{{cursor:pointer;font-weight:800;font-size:18px;list-style:none;display:flex;justify-content:space-between;gap:12px}}
summary::-webkit-details-marker{{display:none}}summary:after{{content:"+";color:var(--o);font-size:26px;line-height:1}}
details[open] summary:after{{content:"–"}}details p{{margin:12px 0 0;color:#4a4670}}
footer{{padding:34px 0 120px;text-align:center;font-size:13px;color:#8a86a8}}footer p{{max-width:760px;margin:0 auto 8px}}
.sticky{{position:fixed;left:0;right:0;bottom:0;z-index:50;padding:12px 16px calc(14px + env(safe-area-inset-bottom));background:rgba(243,240,251,.94);backdrop-filter:blur(8px);border-top:1px solid var(--line);display:none;transform:translateY(120%);transition:transform .25s}}
.sticky.on{{transform:none}}.sticky .cta{{width:100%;font-size:17px;padding:15px 20px}}
@media (max-width:860px){{
 .hero .grid,.vidas,.feat,.bonus .wrap,.three{{grid-template-columns:1fr}}
 .visual{{height:430px;order:-1}}
 .stats{{grid-template-columns:1fr 1fr}}.prev{{grid-template-columns:1fr 1fr}}
 .bonus .wrap{{text-align:center}}.dice{{font-size:96px}}
 section{{padding:58px 0}}.cta{{width:100%}}.sticky{{display:block}}
 .mini svg{{width:48px;height:48px}}
}}
</style></head><body>

<header class="grad hero"><div class="wrap grid">
 <div>
  <span class="pill">◆ NOVO E-BOOK · 10 VIDAS SIMULADAS</span>
  <div class="pre">TENTANDO ME TORNAR…</div>
  <h1>VIDAS<span>IMPOSSÍVEIS</span></h1>
  <p class="sub">E se você pudesse apertar "envelhecer" e acompanhar uma vida inteira, ano por ano, tentando chegar a um objetivo impossível? 10 vidas completas no estilo dos simuladores de vida, do nascimento ao fim.</p>
  <ul class="checks">
   <li>10 vidas contadas ano a ano, com escolhas, azares e conquistas</li>
   <li>1 vida bônus em que VOCÊ decide, com 9 finais secretos</li>
   <li>Fichas e desafios para jogar no seu simulador</li>
  </ul>
  {cta("Quero viver essas vidas", "big")}
  <div class="safe"><span>🔒 Compra segura pela Hotmart</span><span>⚡ Acesso por e-mail após a aprovação</span></div>
 </div>
 <div class="visual">
  {minis}
  <div class="book"><img src="{capa}" alt="Capa do e-book Vidas Impossíveis"></div>
  <div class="bub">Vivi <b>10 vidas</b> impossíveis!</div>
  <div class="char"><img src="{pers}" alt="Personagem do canal"></div>
 </div>
</div></header>

<div class="wrap"><div class="stats">
 <div class="card stat"><div class="n">10</div><div class="t">VIDAS</div></div>
 <div class="card stat"><div class="n">9</div><div class="t">FINAIS SECRETOS</div></div>
 <div class="card stat"><div class="n">80</div><div class="t">PÁGINAS</div></div>
 <div class="card stat"><div class="n">12</div><div class="t">DESAFIOS</div></div>
</div></div>

<section><div class="wrap">
 <div class="center"><div class="k">◆ Escolha sua vida</div><h2>10 sonhos impossíveis. <em>Será que dá?</em></h2></div>
 <div class="vidas">{vidas}</div>
 <div class="center">{cta("Quero ler todas as vidas")}</div>
</div></section>

<section style="padding-top:20px"><div class="wrap">
 <div class="center"><div class="k">◆ Igual ao simulador</div><h2>Cada vida, <em>ano por ano</em></h2></div>
 <ul class="feat">
  <li><i>📅</i>Registro ano a ano, igual ao simulador</li>
  <li><i>🤔</i>Cartões de escolha: pense no que você faria antes de ver a decisão</li>
  <li><i>📊</i>Barras de felicidade, saúde, inteligência e aparência mudando ao longo da vida</li>
  <li><i>👾</i>Personagens em pixel art que envelhecem a cada fase</li>
  <li><i>🪦</i>Cartão de fim de vida: profissão, patrimônio, família e se o objetivo foi cumprido</li>
  <li><i>📱</i>Diagramado para ler no celular</li>
 </ul>
 <div class="prev">{prev}</div>
</div></section>

<section class="grad bonus"><div class="wrap">
 <div class="dice">🎲</div>
 <div>
  <div class="k" style="color:#fff">◆ Bônus</div>
  <h2>Vida #11: VOCÊ decide</h2>
  <p>Nesta vida, quem escolhe é você. Leia, decida e pule para a seção indicada. São 9 finais secretos: virar maestro, goleiro da seleção, cientista premiado… ou acabar famoso e infeliz. Quantos você consegue encontrar?</p>
  {cta("Quero descobrir meu final")}
 </div>
</div></section>

<section><div class="wrap">
 <div class="center"><div class="k">◆ Sua vez</div><h2>Não é <em>só para ler</em></h2></div>
 <div class="three">
  <div class="card"><div class="e">✍️</div><h3>Crie sua própria vida</h3><p>Uma ficha para registrar as vidas que você joga no seu simulador.</p></div>
  <div class="card"><div class="e">🎯</div><h3>12 vidas-desafio</h3><p>Ideias para tentar no jogo, gravar ou desafiar os amigos.</p></div>
  <div class="card"><div class="e">🏆</div><h3>Hall da Fama</h3><p>As 10 vidas lado a lado: quem chegou mais longe?</p></div>
 </div>
</div></section>

<section id="oferta" style="padding-top:20px"><div class="wrap">
 <div class="offer">
  <img src="{capa}" alt="Vidas Impossíveis">
  <div class="k">◆ Acesso completo</div>
  <h2 style="font-size:36px">Vidas Impossíveis</h2>
  <ul>
   <li>E-book completo em PDF (80 páginas)</li>
   <li>10 vidas completas, do nascimento ao fim</li>
   <li>Vida bônus "Você decide", com 9 finais secretos</li>
   <li>Ficha "Crie sua própria vida" + 12 desafios</li>
   <li>Feito para ler no celular</li>
  </ul>
  {cta("Quero meu acesso agora", "big")}
  <div class="safe"><span>🔒 Pagamento seguro Hotmart</span><span>📩 Acesso enviado por e-mail</span></div>
 </div>
</div></section>

<section style="padding-top:20px"><div class="wrap">
 <div class="center"><div class="k">◆ Dúvidas</div><h2>Perguntas <em>frequentes</em></h2></div>
 <div class="faq">{faq}</div>
 <div class="center" style="margin-top:42px">{cta("Começar minha primeira vida")}</div>
</div></section>

<footer><div class="wrap">
 <p>© 2026 Vidas Impossíveis. Produto digital independente, vendido e entregue pela Hotmart.</p>
 <p>Obra de ficção inspirada no gênero dos simuladores de vida. Não é afiliada, patrocinada nem aprovada pela Candywriter LLC, desenvolvedora do BitLife, nem por outra empresa. BitLife é marca de seus respectivos donos.</p>
</div></footer>

<div class="sticky" id="sticky">{cta("Quero meu livro")}</div>
<script>
(function(){{var s=document.getElementById('sticky'),h=document.querySelector('.hero');
function u(){{try{{s.classList.toggle('on',window.scrollY>h.offsetHeight*0.8)}}catch(e){{}}}}
window.addEventListener('scroll',u,{{passive:true}});u();}})();
</script>
</body></html>"""
    out = os.path.join(HERE, "index.html")
    open(out, "w", encoding="utf-8").write(html)
    print("OK", out, f"{len(html) / 1024:.0f} KB", html.count(CHECKOUT), "links")


if __name__ == "__main__":
    main()
