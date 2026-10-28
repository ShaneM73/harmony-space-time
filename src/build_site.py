"""Build the web app from the template and the bundled data.
  docs/index.html      -> self-contained page for GitHub Pages (vendored three.js + d3)
  build/artifact.html  -> same page for publishing as a claude.ai artifact (libraries from cdnjs)"""
import os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl = open(f"{ROOT}/src/app_template.html", encoding="utf-8").read()
data = open(f"{ROOT}/data/harmony_data.json", encoding="utf-8").read().replace("</", "<\\/")
import base64
_meta = json.load(open(f"{ROOT}/data/basemap_meta.json"))
_meta["terrain"] = "data:image/png;base64," + base64.b64encode(open(f"{ROOT}/data/terrain.png", "rb").read()).decode()
_meta["texture"] = "data:image/jpeg;base64," + base64.b64encode(open(f"{ROOT}/data/map_texture.jpg", "rb").read()).decode()
basemap = json.dumps(_meta, separators=(",", ":"))

pages = f'<script src="vendor/three.min.js"></script>\n<script src="vendor/d3.min.js"></script>'
cdn = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n'
       '<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>')

body = tpl.replace("__DATA__", data).replace("__BASEMAP__", basemap)
os.makedirs(f"{ROOT}/docs", exist_ok=True); os.makedirs(f"{ROOT}/build", exist_ok=True)
with open(f"{ROOT}/docs/index.html", "w", encoding="utf-8") as fh:
    fh.write('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
             + body.replace("__LIBS__", pages).split("<style>")[0]  # title/meta/link
             + "<style>" + body.replace("__LIBS__", pages).split("<style>", 1)[1].split("</style>", 1)[0] + "</style>\n</head>\n<body>\n"
             + body.replace("__LIBS__", pages).split("</style>", 1)[1] + "\n</body>\n</html>\n")
with open(f"{ROOT}/build/artifact.html", "w", encoding="utf-8") as fh:
    fh.write(body.replace("__LIBS__", cdn))
print("docs/index.html", os.path.getsize(f"{ROOT}/docs/index.html"), "bytes; build/artifact.html", os.path.getsize(f"{ROOT}/build/artifact.html"), "bytes")
