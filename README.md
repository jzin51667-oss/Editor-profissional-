# Editor-profissional-
## Vídeo editado

- `output/video_editado.mp4` — vídeo final com elementos na tela
- `scripts/editar_video.py` — script que gera a edição (Pillow + ffmpeg)
- `data/transcricao.json` — transcrição com tempo de cada palavra (usada nas legendas)

Para gerar de novo:

```
python3 scripts/editar_video.py ENTRADA.mp4 output/video_editado.mp4 data/transcricao.json
```
