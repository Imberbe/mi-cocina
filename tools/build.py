"""Genera index.html (la app instalable de GitHub Pages) a partir de src/mi-cocina.html,
que es la misma página que se publica en Claude. Sube también la versión de la caché (sw.js)
para que los móviles descarguen la versión nueva.

Uso:  python3 tools/build.py
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
src = (ROOT / "src" / "mi-cocina.html").read_text(encoding="utf-8")
src = src.replace("Guardado solo en este dispositivo.", "Guardado en este móvil.")

HEAD = """<!doctype html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#55731B">
<meta name="description" content="Menú semanal, recetas paso a paso y lista de la compra.">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="icon-192.png">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>
"""
TAIL = """
<script>if("serviceWorker" in navigator){addEventListener("load",()=>navigator.serviceWorker.register("sw.js").catch(()=>{}));}</script>
</body></html>
"""
(ROOT / "index.html").write_text(HEAD + src + TAIL, encoding="utf-8")

sw = ROOT / "sw.js"
txt = sw.read_text(encoding="utf-8")
txt = re.sub(r"mi-cocina-v(\d+)", lambda m: f"mi-cocina-v{int(m.group(1)) + 1}", txt, count=1)
sw.write_text(txt, encoding="utf-8")
print("index.html generado;", re.search(r"mi-cocina-v\d+", txt).group(0))
