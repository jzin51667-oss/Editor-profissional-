#!/usr/bin/env python3
"""Gera a página de vendas (index.html, arquivo único com imagens embutidas).

Uso: python3 pagina-de-vendas/gerar.py
Todos os botões de compra apontam para CHECKOUT.
"""
import base64
import io
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "ebook"))
import icons  # noqa: E402

CHECKOUT = "https://pay.hotmart.com/U108383162C?checkoutMode=10"
PDF = os.path.join(ROOT, "ebook", "dist", "Guia-dos-Segredos-dos-Games.pdf")
PERSONAGEM = os.path.join(ROOT, "ebook", "divulgacao", "personagem.png")


def data_uri(img, fmt="WEBP", quality=82, width=None):
    if width and img.width > width:
        img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, fmt, quality=quality, method=6)
    return f"data:image/{fmt.lower()};base64," + base64.b64encode(buf.getvalue()).decode()


def page_img(n, width):
    out = os.path.join(HERE, f"_p{n}")
    subprocess.run(["pdftoppm", "-r", "200", "-png", "-f", str(n), "-l", str(n), "-singlefile", PDF, out],
                   check=True, stderr=subprocess.DEVNULL)
    img = Image.open(out + ".png").convert("RGB")
    os.remove(out + ".png")
    return data_uri(img, width=width)


def ico(name, size, glow=None):
    return icons.svg(name, size, glow)


def main():
    capa = page_img(1, 760)
    previews = [(page_img(n, 520), t) for n, t in [
        (11, "Minecraft: nomes que transformam mobs"),
        (24, "Abertura de fase: Blox Fruits"),
        (55, "Lendas com selo de veredito"),
        (67, "O Desafio de 7 Dias"),
    ]]
    pers = data_uri(Image.open(PERSONAGEM), width=520, quality=88)

    fases = [
        ("pickaxe", "Minecraft", "Nomes que transformam mobs, raridades como o axolote azul, a melhor altura para diamantes e como passar pelo Warden."),
        ("avatar", "Roblox", "A história escondida da plataforma, o truque das insígnias para achar segredos e o guia das entidades de DOORS."),
        ("fruit", "Blox Fruits", "Os três mares, tipos de fruta, as habilidades que você precisa comprar primeiro e builds para evoluir rápido."),
        ("heart", "BitLife", "Estratégia para cada fase da vida, o caminho até a presidência e vidas-desafio exclusivas."),
        ("car", "GTA", "O coração escondido de Liberty City, o mistério do Monte Chiliad, códigos clássicos e o que é golpe no celular."),
        ("button", "Among Us", "Todos os papéis especiais, mecânicas que o tutorial não conta e táticas de tripulante e impostor."),
        ("phone", "Jogos mobile", "O Pikachu inicial e os nomes secretos das Eevees no Pokémon GO, manhas do Subway Surfers e mais."),
        ("ghost", "Lendas", "Herobrine, Polybius, o Mew debaixo do caminhão… cada lenda com veredito: mito, real ou parcial."),
        ("magnifier", "Método do Explorador", "As técnicas para descobrir segredos em qualquer jogo, até nos que ainda vão ser lançados."),
    ]
    fases_html = "".join(
        f'<div class="fase"><div class="fi">{ico(i, 52)}</div><div><h3>{t}</h3><p>{d}</p></div></div>'
        for i, t, d in fases)
    prev_html = "".join(f'<figure><img src="{src}" alt="{t}"><figcaption>{t}</figcaption></figure>' for src, t in previews)

    faq = [
        ("Como recebo o e-book?", "Depois que o pagamento é aprovado, a Hotmart envia o acesso para o seu e-mail. O guia é um PDF que você pode baixar e guardar."),
        ("Dá para ler no celular?", "Sim. O guia foi diagramado em formato de livro de bolso, pensado para ler no celular, no tablet ou no computador. As páginas de missões também podem ser impressas."),
        ("Tem hack, programa ou “moedas grátis”?", "Não. Nada no guia coloca sua conta em risco. Tudo funciona jogando normalmente, e o guia ainda ensina a reconhecer golpes."),
        ("Preciso jogar todos os jogos?", "Não. Cada fase é independente: você pode ir direto para os jogos que mais curte. O Método do Explorador vale para qualquer jogo."),
        ("As informações estão atualizadas?", "Foram pesquisadas e conferidas para as versões do fim de 2026. Quando algo depende da versão ou da plataforma, o guia avisa."),
        ("É um produto oficial dos jogos?", "Não. É um guia independente, feito por fãs para fãs, sem ligação com as empresas dos jogos citados."),
    ]
    faq_html = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in faq)

    cta = lambda txt, extra="": f'<a class="cta {extra}" href="{CHECKOUT}" rel="noopener">{txt}<span>→</span></a>'

    html = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Guia dos Segredos dos Games</title>
<meta name="description" content="Segredos, easter eggs, lendas e desafios de Minecraft, Roblox, Blox Fruits, BitLife, GTA, Among Us e jogos mobile. 40 missões e desafio de 7 dias.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=JetBrains+Mono:wght@700;800&display=swap" rel="stylesheet">
<style>
:root{{--bg:#07081a;--panel:#11142e;--line:#272f63;--text:#cfd5f5;--dim:#8f97c2;--cyan:#22d3ee;--blue:#3b82f6;--purple:#8b5cf6;--magenta:#e879f9;--yellow:#facc15;--green:#34d399;--red:#f43f5e}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}
html,body{{overflow-x:clip}}
body{{margin:0;background:var(--bg);color:var(--text);font:400 17px/1.6 Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased}}
img{{max-width:100%;display:block}}
.wrap{{max-width:1080px;margin:0 auto;padding:0 22px}}
.mono{{font-family:"JetBrains Mono",monospace;font-weight:800;letter-spacing:.18em;font-size:13px;color:var(--cyan);text-transform:uppercase}}
h1,h2,h3{{color:#fff;margin:0;line-height:1.08;letter-spacing:-.01em}}
h2{{font-size:clamp(30px,4.6vw,46px);font-weight:900;margin:10px 0 14px}}
h2 em{{font-style:normal;background:linear-gradient(90deg,var(--cyan),var(--purple));-webkit-background-clip:text;color:transparent}}
section{{padding:80px 0;position:relative}}
.center{{text-align:center}}
.lead{{font-size:19px;color:#e2e6ff;max-width:720px}}
.center .lead{{margin:0 auto}}

/* HERO */
.hero{{position:relative;padding:46px 0 70px;overflow:hidden;background:
 radial-gradient(circle at 72% 40%,rgba(139,92,246,.5),transparent 40%),
 radial-gradient(circle at 12% 70%,rgba(34,211,238,.28),transparent 38%),
 radial-gradient(circle at 90% 0,rgba(59,130,246,.4),transparent 35%),
 linear-gradient(180deg,#0a0b24,#120a2e 70%,var(--bg))}}
.hero:after{{content:"";position:absolute;left:-30%;right:-30%;bottom:0;height:260px;
 background-image:linear-gradient(rgba(34,211,238,.35) 2px,transparent 2px),linear-gradient(90deg,rgba(34,211,238,.35) 2px,transparent 2px);
 background-size:64px 64px;transform:perspective(380px) rotateX(62deg);transform-origin:bottom;-webkit-mask-image:linear-gradient(transparent,#000 70%);pointer-events:none}}
.hero .grid{{display:grid;grid-template-columns:1.05fr .95fr;gap:30px;align-items:center;position:relative;z-index:1}}
.pill{{display:inline-flex;gap:8px;align-items:center;border:1px solid rgba(165,243,252,.45);background:rgba(10,12,32,.6);border-radius:999px;padding:7px 14px}}
.hero h1{{font-size:clamp(40px,6.4vw,72px);font-weight:900;margin:18px 0 18px;text-shadow:0 0 30px rgba(34,211,238,.35)}}
.hero h1 b{{background:linear-gradient(180deg,#fff,#a5f3fc 35%,#22d3ee 60%,#8b5cf6);-webkit-background-clip:text;color:transparent}}
.hero .sub{{font-size:20px;color:#e0e6ff;margin:0 0 26px;max-width:560px}}
.checks{{list-style:none;padding:0;margin:0 0 30px;display:grid;gap:9px}}
.checks li{{display:flex;gap:10px;align-items:flex-start;font-weight:600;color:#fff}}
.checks li:before{{content:"✓";flex:none;width:24px;height:24px;border-radius:7px;background:linear-gradient(135deg,var(--cyan),var(--purple));color:#fff;font:800 14px/24px Inter;text-align:center;margin-top:1px}}
.visual{{position:relative;height:560px}}
.book{{position:absolute;right:0;top:10px;width:min(380px,74%);transform:rotate(6deg);border-radius:12px;overflow:hidden;
 box-shadow:0 0 0 3px rgba(165,243,252,.5),0 0 70px rgba(139,92,246,.85),0 40px 80px rgba(0,0,0,.7);animation:float 6s ease-in-out infinite}}
.book:after{{content:"";position:absolute;inset:0;background:linear-gradient(115deg,rgba(255,255,255,.2),transparent 35%)}}
.char{{position:absolute;left:0;bottom:0;width:min(330px,62%);filter:drop-shadow(0 0 24px rgba(34,211,238,.5)) drop-shadow(0 18px 26px rgba(0,0,0,.6))}}
.char img{{-webkit-mask-image:linear-gradient(#000 85%,transparent)}}
.bubble{{position:absolute;left:4%;top:20px;background:#fff;color:#14112e;border:4px solid #0b0d1a;border-radius:22px;padding:14px 18px;font:800 18px/1.2 Inter;box-shadow:6px 6px 0 var(--cyan);max-width:220px;z-index:2}}
.bubble:after{{content:"";position:absolute;left:40px;bottom:-17px;width:26px;height:26px;background:#fff;border-right:4px solid #0b0d1a;border-bottom:4px solid #0b0d1a;transform:rotate(45deg)}}
.bubble b{{color:#7c3aed}}
@keyframes float{{0%,100%{{transform:rotate(6deg) translateY(0)}}50%{{transform:rotate(5deg) translateY(-12px)}}}}

.cta{{display:inline-flex;align-items:center;justify-content:center;gap:12px;text-decoration:none;color:#fff;font:900 20px Inter;letter-spacing:.02em;
 padding:20px 34px;border-radius:999px;background:linear-gradient(90deg,#06b6d4,#8b5cf6,#d946ef);border:3px solid #fff;
 box-shadow:0 0 34px rgba(217,70,239,.55),0 8px 0 #3b1d8f;transition:transform .15s,box-shadow .15s;text-transform:uppercase}}
.cta span{{font-size:24px;transition:transform .15s}}
.cta:hover{{transform:translateY(-3px);box-shadow:0 0 50px rgba(217,70,239,.8),0 11px 0 #3b1d8f}}
.cta:hover span{{transform:translateX(4px)}}
.cta:active{{transform:translateY(4px);box-shadow:0 0 20px rgba(217,70,239,.6),0 4px 0 #3b1d8f}}
.cta.big{{font-size:22px;padding:24px 40px}}
.safe{{display:flex;flex-wrap:wrap;gap:16px;margin-top:16px;color:var(--dim);font-size:14px;font-weight:600}}
.center .safe{{justify-content:center}}

/* STRIP */
.strip{{border-top:1px solid var(--line);border-bottom:1px solid var(--line);background:#0b0d22;padding:18px 0}}
.strip .wrap{{display:flex;flex-wrap:wrap;gap:12px 30px;justify-content:center}}
.strip span{{font:800 14px "JetBrains Mono";letter-spacing:.14em;color:#9aa3d6}}

/* stats */
.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:36px}}
.stat{{background:linear-gradient(160deg,#1c1f4b,#10122a);border:1px solid #303880;border-radius:20px;padding:22px 14px;text-align:center}}
.stat .n{{font:900 46px/1 Inter;color:var(--cyan)}}
.stat .t{{font:800 13px "JetBrains Mono";letter-spacing:.1em;color:#c7cdf0;margin-top:8px}}

/* para quem */
.two{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:30px}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:20px;padding:26px}}
.card h3{{font-size:22px;margin:14px 0 8px}}
.card p{{margin:0;color:var(--text)}}

/* fases */
.fases{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:34px}}
.fase{{display:flex;gap:14px;background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:18px;transition:border-color .2s,transform .2s}}
.fase:hover{{border-color:var(--purple);transform:translateY(-3px)}}
.fase .fi{{flex:none;width:64px;height:64px;border-radius:14px;background:#0a0c22;display:grid;place-items:center;border:1px solid #2b3270}}
.fase h3{{font-size:19px;margin:2px 0 4px}}
.fase p{{margin:0;font-size:15px;line-height:1.5;color:#b9c0e6}}

/* game */
.gamebox{{display:grid;grid-template-columns:1fr 1fr;gap:30px;align-items:center;background:linear-gradient(150deg,#1b1442,#0e1130 70%);border:2px solid #5b4bc4;border-radius:28px;padding:40px;margin-top:10px}}
.xpl{{display:grid;gap:9px}}
.xpr{{display:flex;align-items:center;gap:12px;background:rgba(9,11,28,.7);border:1px solid #2f3775;border-radius:12px;padding:10px 14px}}
.xpr b{{font:900 22px Inter;color:var(--yellow);width:26px}}
.xpr span{{flex:1;color:#fff;font-weight:700}}
.xpr small{{font:800 13px "JetBrains Mono";color:var(--cyan)}}
.feat{{list-style:none;padding:0;margin:18px 0 0;display:grid;gap:10px}}
.feat li{{display:flex;gap:10px;font-weight:600;color:#fff}}
.feat li i{{font-style:normal}}

/* previews */
.prev{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:34px}}
.prev figure{{margin:0}}
.prev img{{border-radius:12px;border:1px solid #333c7a;box-shadow:0 20px 40px rgba(0,0,0,.5);transition:transform .2s}}
.prev img:hover{{transform:scale(1.03)}}
.prev figcaption{{font-size:13px;color:var(--dim);text-align:center;margin-top:10px;font-weight:600}}

/* trust */
.trust{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:30px}}
.trust .card{{text-align:center}}
.trust .em{{font-size:38px}}

/* offer */
.offer{{max-width:640px;margin:0 auto;background:linear-gradient(160deg,#1a1440,#0d1030 70%);border:2px solid var(--yellow);border-radius:28px;padding:38px 30px;text-align:center;
 box-shadow:0 0 0 6px rgba(250,204,21,.08),0 30px 60px rgba(0,0,0,.5)}}
.offer ul{{text-align:left;list-style:none;padding:0;margin:22px 0 28px;display:grid;gap:9px}}
.offer li{{display:flex;gap:10px;color:#fff;font-weight:600}}
.offer li:before{{content:"◆";color:var(--yellow)}}

/* faq */
.faq{{max-width:760px;margin:30px auto 0;display:grid;gap:12px}}
details{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px 22px}}
summary{{cursor:pointer;color:#fff;font-weight:800;font-size:18px;list-style:none;display:flex;justify-content:space-between;gap:12px}}
summary::-webkit-details-marker{{display:none}}
summary:after{{content:"+";color:var(--cyan);font-size:24px;line-height:1}}
details[open] summary:after{{content:"–"}}
details p{{margin:12px 0 0}}

footer{{border-top:1px solid var(--line);padding:34px 0 120px;color:#6f77a6;font-size:13px;text-align:center}}
footer p{{max-width:760px;margin:0 auto 8px}}

/* sticky mobile */
.sticky{{position:fixed;left:0;right:0;bottom:0;z-index:50;padding:12px 16px calc(12px + env(safe-area-inset-bottom));background:rgba(7,8,26,.92);backdrop-filter:blur(8px);
 border-top:1px solid #2b3270;display:none;transform:translateY(110%);transition:transform .25s}}
.sticky.on{{transform:none}}
.sticky .cta{{width:100%;font-size:17px;padding:16px 20px}}

@media (max-width:860px){{
 .hero .grid,.gamebox,.two{{grid-template-columns:1fr}}
 .visual{{height:440px;order:-1}}
 .fases{{grid-template-columns:1fr}}
 .prev{{grid-template-columns:1fr 1fr}}
 .stats{{grid-template-columns:1fr 1fr}}
 .trust{{grid-template-columns:1fr}}
 .gamebox{{padding:26px}}
 section{{padding:60px 0}}
 .cta{{width:100%}}
 .sticky{{display:block}}
}}
</style></head>
<body>

<header class="hero"><div class="wrap grid">
 <div>
  <span class="pill mono">◆ E-book · Edição 2026</span>
  <h1>Todo jogo esconde algo.<br><b>Agora você vai descobrir.</b></h1>
  <p class="sub">O <strong>Guia dos Segredos dos Games</strong> reúne easter eggs, mecânicas escondidas, lendas e desafios dos jogos que você mais joga, em um guia que você joga junto.</p>
  <ul class="checks">
   <li>Minecraft, Roblox, Blox Fruits, BitLife, GTA, Among Us e jogos mobile</li>
   <li>40 missões com XP e níveis, do Novato à Lenda dos Games</li>
   <li>Desafio de 7 dias, diário do explorador e quiz final</li>
  </ul>
  {cta("Quero meu guia agora", "big")}
  <div class="safe"><span>🔒 Compra segura pela Hotmart</span><span>⚡ Acesso por e-mail após a aprovação</span></div>
 </div>
 <div class="visual">
  <div class="book"><img src="{capa}" alt="Capa do Guia dos Segredos dos Games"></div>
  <div class="bubble">Descobri os <b>segredos</b> dos seus jogos!</div>
  <div class="char"><img src="{pers}" alt="Personagem do canal"></div>
 </div>
</div></header>

<div class="strip"><div class="wrap"><span>MINECRAFT</span><span>ROBLOX</span><span>BLOX FRUITS</span><span>BITLIFE</span><span>GTA</span><span>AMONG US</span><span>POKÉMON GO</span><span>SUBWAY SURFERS</span></div></div>

<section><div class="wrap center">
 <div class="mono">◆ Por que este guia</div>
 <h2>Você já jogou muito.<br><em>Mas já viu tudo?</em></h2>
 <p class="lead">Tem nome que deixa um mob de cabeça para baixo no Minecraft. Tem um coração batendo escondido numa estátua de GTA. Tem um jeito de começar Pokémon GO com Pikachu. A maioria dos jogadores passa centenas de horas nesses jogos sem saber nada disso.</p>
 <div class="stats">
  <div class="stat"><div class="n">12</div><div class="t">FASES</div></div>
  <div class="stat"><div class="n">40</div><div class="t">MISSÕES</div></div>
  <div class="stat"><div class="n">79</div><div class="t">PÁGINAS</div></div>
  <div class="stat"><div class="n">7</div><div class="t">DIAS DE DESAFIO</div></div>
 </div>
</div></section>

<section style="padding-top:20px"><div class="wrap">
 <div class="center"><div class="mono">◆ Para quem é</div><h2>Feito para <em>dois tipos</em> de jogador</h2></div>
 <div class="two">
  <div class="card">{ico("controller", 54)}<h3>Quem joga de verdade</h3><p>Estratégias, mecânicas que o tutorial não explica, builds, raridades e atalhos que economizam horas de jogo.</p></div>
  <div class="card">{ico("ghost", 54)}<h3>Quem ama curiosidades</h3><p>Histórias de bastidores, lendas investigadas, easter eggs famosos e fatos para contar para os amigos.</p></div>
 </div>
</div></section>

<section style="padding-top:30px"><div class="wrap">
 <div class="center"><div class="mono">◆ O que tem dentro</div><h2>Uma fase para cada <em>universo</em></h2>
 <p class="lead">Cada capítulo é uma fase, com abertura própria, segredos explicados passo a passo e missões para você testar no jogo.</p></div>
 <div class="fases">{fases_html}</div>
</div></section>

<section><div class="wrap">
 <div class="gamebox">
  <div>
   <div class="mono" style="color:var(--magenta)">◆ Não é só leitura</div>
   <h2>Um guia que você <em>joga</em></h2>
   <p>Cada missão completada dá XP. Some seus pontos e suba de nível até virar Lenda dos Games.</p>
   <ul class="feat">
    <li><i>🎯</i> 40 missões com dificuldade e recompensa</li>
    <li><i>📅</i> Desafio de 7 dias, uma missão por dia</li>
    <li><i>📓</i> Diário do Explorador para registrar descobertas</li>
    <li><i>🏆</i> Rankings pessoais e placar de XP</li>
    <li><i>💀</i> Quiz do Chefão com 20 perguntas e certificado</li>
   </ul>
  </div>
  <div class="xpl">
   <div class="xpr"><b>1</b><span>Novato Curioso</span><small>0 XP</small></div>
   <div class="xpr"><b>2</b><span>Explorador</span><small>150 XP</small></div>
   <div class="xpr"><b>3</b><span>Caçador de Segredos</span><small>400 XP</small></div>
   <div class="xpr"><b>4</b><span>Mestre dos Easter Eggs</span><small>800 XP</small></div>
   <div class="xpr" style="border-color:var(--yellow)"><b>5</b><span>Lenda dos Games</span><small>1.200 XP</small></div>
  </div>
 </div>
</div></section>

<section style="padding-top:20px"><div class="wrap">
 <div class="center"><div class="mono">◆ Espie por dentro</div><h2>Diagramado como um <em>jogo</em></h2>
 <p class="lead">Visual escuro com neon, ilustrações em pixel art feitas exclusivamente para o guia e caixas de curiosidade, atenção e dica em cada fase.</p></div>
 <div class="prev">{prev_html}</div>
 <div class="center" style="margin-top:40px">{cta("Quero explorar todas as fases")}</div>
</div></section>

<section><div class="wrap">
 <div class="center"><div class="mono">◆ Pode confiar</div><h2>Sem hack. Sem golpe. <em>Sem enrolação.</em></h2></div>
 <div class="trust">
  <div class="card"><div class="em">🛡️</div><h3>Conta segura</h3><p>Nada de programa externo, “moedas grátis” ou trapaça online. Tudo funciona jogando normalmente.</p></div>
  <div class="card"><div class="em">🔍</div><h3>Informação checada</h3><p>Pesquisado e conferido para as versões de 2026, com aviso quando algo depende da versão do jogo.</p></div>
  <div class="card"><div class="em">📱</div><h3>Lê em qualquer lugar</h3><p>PDF em formato de bolso, feito para o celular. Baixe uma vez e leia quando quiser.</p></div>
 </div>
</div></section>

<section id="oferta"><div class="wrap">
 <div class="offer">
  {ico("chest", 96, 8)}
  <div class="mono" style="color:var(--yellow);margin-top:14px">◆ Acesso completo</div>
  <h2 style="font-size:34px">Guia dos Segredos dos Games</h2>
  <ul>
   <li>E-book completo em PDF (79 páginas)</li>
   <li>12 fases: Minecraft, Roblox, Blox Fruits, BitLife, GTA, Among Us, mobile, lendas e mais</li>
   <li>40 missões com sistema de XP e níveis</li>
   <li>Desafio de 7 dias + Diário do Explorador</li>
   <li>Quiz do Chefão com gabarito comentado e certificado</li>
  </ul>
  {cta("Quero meu acesso agora", "big")}
  <div class="safe" style="justify-content:center"><span>🔒 Pagamento seguro Hotmart</span><span>📩 Acesso enviado por e-mail</span></div>
 </div>
</div></section>

<section style="padding-top:20px"><div class="wrap">
 <div class="center"><div class="mono">◆ Dúvidas</div><h2>Perguntas <em>frequentes</em></h2></div>
 <div class="faq">{faq_html}</div>
 <div class="center" style="margin-top:44px">{cta("Começar minha jornada")}</div>
</div></section>

<footer><div class="wrap">
 <p>© 2026 Guia dos Segredos dos Games. Produto digital independente, vendido e entregue pela Hotmart.</p>
 <p>Este guia não é afiliado, patrocinado nem aprovado pelas empresas dos jogos citados. Minecraft, Roblox, Blox Fruits, BitLife, Grand Theft Auto, Among Us, Pokémon GO, Subway Surfers e demais marcas pertencem aos seus respectivos donos.</p>
</div></footer>

<div class="sticky" id="sticky">{cta("Quero meu guia")}</div>

<script>
(function(){{
  var s=document.getElementById('sticky'),h=document.querySelector('.hero');
  function u(){{ try{{ s.classList.toggle('on', window.scrollY > h.offsetHeight*0.8); }}catch(e){{}} }}
  window.addEventListener('scroll',u,{{passive:true}}); u();
}})();
</script>
</body></html>"""
    out = os.path.join(HERE, "index.html")
    open(out, "w", encoding="utf-8").write(html)
    print("OK", out, f"{len(html) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
