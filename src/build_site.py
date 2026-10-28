"""Assemble the site: copy the data the pages fetch into docs/data, and derive build/artifact.html
(the cube page without the document wrapper) for publishing as a claude.ai artifact with its files."""
import os, re, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(f"{ROOT}/docs/data", exist_ok=True); os.makedirs(f"{ROOT}/build", exist_ok=True)
for f in ["harmony_data.json", "basemap_meta.json", "terrain.png", "map_texture_dark.jpg", "map_texture_light.jpg"]:
    shutil.copyfile(f"{ROOT}/data/{f}", f"{ROOT}/docs/data/{f}")
html = open(f"{ROOT}/docs/index.html", encoding="utf-8").read()
head = re.search(r"<head>(.*?)</head>", html, re.S).group(1)
body = re.search(r"<body>(.*?)</body>", html, re.S).group(1)
keep = "\n".join(l for l in head.splitlines() if "<title>" in l or "stylesheet" in l or 'name="description"' in l)
open(f"{ROOT}/build/artifact.html", "w", encoding="utf-8").write(keep + "\n" + body)
print("docs/data ready;", "build/artifact.html", os.path.getsize(f"{ROOT}/build/artifact.html"), "bytes")
