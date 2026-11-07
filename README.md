# Editor-profissional-
## Vídeo editado

- `output/video_editado.mp4` — vídeo final com elementos na tela
- `scripts/editar_video.py` — script que gera a edição (Pillow + ffmpeg)
- `data/transcricao.json` — transcrição com tempo de cada palavra (usada nas legendas)

Para gerar de novo:

```
python3 scripts/editar_video.py ENTRADA.mp4 output/video_editado.mp4 data/transcricao.json
```

## E-book: Guia dos Segredos dos Games

- `ebook/dist/Guia-dos-Segredos-dos-Games.pdf` — PDF final (79 páginas, A5)
- `ebook/capitulos/` — texto de cada fase em HTML (edite aqui)
- `ebook/style.css` — identidade visual · `ebook/icons.py` — ícones em pixel art originais
- Gerar de novo: `python3 ebook/build.py` (requer Playwright/Chromium e poppler-utils)
