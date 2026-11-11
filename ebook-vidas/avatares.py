"""Avatares em pixel art (16x16) gerados por código, originais deste e-book.

avatar(pele, cabelo, cor_cabelo, roupa, acessorio, fase) -> SVG
fase: "bebe", "jovem", "adulto", "idoso"
"""

PELES = {"clara": "#f5d0b0", "media": "#d9a27a", "morena": "#b07650", "escura": "#7a4a2c"}
CABELOS_COR = {"preto": "#1f1a17", "castanho": "#5b3a1e", "loiro": "#e8c25a", "ruivo": "#c2531f",
               "rosa": "#f472b6", "azul": "#3b82f6", "cinza": "#b8bcc6", "branco": "#eef0f4"}


def _grid():
    return [[None] * 16 for _ in range(16)]


def _rect(g, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if 0 <= x < 16 and 0 <= y < 16:
                g[y][x] = c


def _px(g, pts, c):
    for x, y in pts:
        if 0 <= x < 16 and 0 <= y < 16:
            g[y][x] = c


def avatar_grid(pele="media", cabelo="curto", cor_cabelo="preto", roupa="#3b82f6", acessorio=None, fase="adulto"):
    g = _grid()
    sk = PELES.get(pele, pele)
    hc = CABELOS_COR.get(cor_cabelo, cor_cabelo)
    if fase == "idoso":
        hc = CABELOS_COR["cinza"] if cor_cabelo not in ("branco",) else hc
    dark = "#1b1b2a"
    # corpo
    if fase == "bebe":
        _rect(g, 4, 13, 11, 15, roupa)
        _rect(g, 7, 12, 8, 12, sk)
    else:
        _rect(g, 2, 13, 13, 15, roupa)
        _rect(g, 3, 12, 12, 12, roupa)
        _rect(g, 7, 11, 8, 12, sk)
        _px(g, [(6, 12), (9, 12)], sk)  # gola em V
    # cabeça
    _rect(g, 5, 4, 10, 10, sk)
    _px(g, [(4, 6), (4, 7), (11, 6), (11, 7)], sk)
    # olhos e boca
    _px(g, [(6, 7), (9, 7)], dark)
    _px(g, [(7, 9), (8, 9)], "#b4423a")
    if fase == "idoso":
        _px(g, [(5, 9), (10, 9)], "#c48a6a" if pele in ("clara", "media") else "#5a3420")
    if fase == "bebe":
        _px(g, [(5, 8), (10, 8)], "#f29a9a")
    # cabelos
    if fase == "bebe":
        _px(g, [(7, 3), (8, 3), (8, 2)], hc)
    elif cabelo == "careca":
        _px(g, [(4, 5), (11, 5)], hc)
    elif cabelo == "curto":
        _rect(g, 5, 2, 10, 3, hc)
        _px(g, [(4, 3), (11, 3), (4, 4), (11, 4), (4, 5), (11, 5), (5, 4), (10, 4)], hc)
    elif cabelo == "longo":
        _rect(g, 5, 2, 10, 3, hc)
        _rect(g, 3, 3, 4, 11, hc)
        _rect(g, 11, 3, 12, 11, hc)
        _px(g, [(5, 4), (6, 4), (10, 4)], hc)
    elif cabelo == "crespo":
        _rect(g, 4, 1, 11, 3, hc)
        _rect(g, 3, 2, 12, 4, hc)
        _px(g, [(3, 5), (12, 5), (4, 5), (11, 5), (5, 4), (10, 4), (6, 0), (9, 0)], hc)
    elif cabelo == "coque":
        _rect(g, 5, 2, 10, 3, hc)
        _rect(g, 6, 0, 9, 1, hc)
        _px(g, [(4, 3), (11, 3), (4, 4), (11, 4), (4, 5), (11, 5)], hc)
    elif cabelo == "rabo":
        _rect(g, 5, 2, 10, 3, hc)
        _px(g, [(4, 3), (4, 4), (4, 5), (11, 3), (11, 4), (12, 4), (12, 5), (13, 6), (13, 7), (13, 8)], hc)
    elif cabelo == "topete":
        _rect(g, 5, 2, 10, 3, hc)
        _rect(g, 6, 0, 10, 1, hc)
        _px(g, [(4, 3), (11, 3), (4, 4), (11, 4)], hc)
    # acessórios
    a = acessorio
    if a == "oculos":
        _px(g, [(5, 7), (6, 7), (9, 7), (10, 7)], dark)
        _px(g, [(7, 7), (8, 7)], dark)
    elif a == "oculos_escuros":
        _rect(g, 5, 6, 10, 7, dark)
    elif a == "estetoscopio":
        _px(g, [(5, 12), (5, 13), (6, 14), (7, 14), (10, 12), (10, 13), (9, 14), (8, 14)], "#cbd5e1")
        _px(g, [(8, 15)], "#94a3b8")
    elif a == "jaleco":
        _rect(g, 2, 13, 5, 15, "#f8fafc")
        _rect(g, 10, 13, 13, 15, "#f8fafc")
        _px(g, [(3, 12), (4, 12), (5, 12), (10, 12), (11, 12), (12, 12)], "#f8fafc")
    elif a == "capacete":
        _rect(g, 3, 1, 12, 3, "#e2e8f0")
        _rect(g, 3, 4, 4, 10, "#e2e8f0")
        _rect(g, 11, 4, 12, 10, "#e2e8f0")
        _rect(g, 4, 11, 11, 11, "#e2e8f0")
        _px(g, [(5, 4), (10, 4)], "#7dd3fc")
    elif a == "coroa":
        _rect(g, 5, 1, 10, 2, "#facc15")
        _px(g, [(5, 0), (7, 0), (8, 0), (10, 0)], "#facc15")
        _px(g, [(7, 1)], "#ef4444")
    elif a == "bone":
        _rect(g, 5, 2, 10, 3, roupa)
        _rect(g, 9, 3, 12, 3, roupa)
    elif a == "fone":
        _px(g, [(4, 2), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (11, 2)], "#111827")
        _rect(g, 3, 5, 4, 8, "#e11d48")
        _rect(g, 11, 5, 12, 8, "#e11d48")
    elif a == "mascara":
        _rect(g, 5, 6, 10, 7, "#111827")
        _px(g, [(6, 7), (9, 7)], "#f8fafc")
        _px(g, [(11, 6), (12, 7)], "#111827")
    elif a == "gravata":
        _px(g, [(7, 12), (8, 12), (7, 13), (8, 13), (7, 14), (8, 14), (8, 15)], "#dc2626")
        _px(g, [(6, 12), (9, 12)], "#f8fafc")
    elif a == "tiara":
        _rect(g, 5, 2, 10, 2, "#facc15")
        _px(g, [(7, 1), (8, 1)], "#38bdf8")
    elif a == "faixa":
        _rect(g, 4, 3, 11, 3, "#ef4444")
    if a == "capa":
        _rect(g, 1, 12, 2, 15, "#dc2626")
        _rect(g, 13, 12, 14, 15, "#dc2626")
        _px(g, [(7, 13), (8, 13), (7, 14), (8, 14)], "#facc15")
    return g


def svg_from_grid(g, size=96, bg=None, radius=0):
    rects = []
    if bg:
        rects.append(f'<rect width="16" height="16" rx="{radius}" fill="{bg}"/>')
    for y, row in enumerate(g):
        x = 0
        while x < 16:
            c = row[x]
            if c is None:
                x += 1
                continue
            run = 1
            while x + run < 16 and row[x + run] == c:
                run += 1
            rects.append(f'<rect x="{x}" y="{y}" width="{run}" height="1" fill="{c}"/>')
            x += run
    return (f'<svg class="av" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="{size}" height="{size}" '
            f'shape-rendering="crispEdges">' + "".join(rects) + "</svg>")


def avatar(size=96, bg=None, radius=0, **kw):
    return svg_from_grid(avatar_grid(**kw), size, bg, radius)
