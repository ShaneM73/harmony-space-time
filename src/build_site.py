"""Derive build/artifact.html (the cube page without the document wrapper) for publishing the app as a
claude.ai artifact with its files. The site itself is the repository root: index.html, app.js, style.css,
findings.html, findings.js, vendor/ and data/ (served by GitHub Pages from the root of main)."""
import os, re, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(f"{ROOT}/build", exist_ok=True)
html = open(f"{ROOT}/index.html", encoding="utf-8").read()
head = re.search(r"<head>(.*?)</head>", html, re.S).group(1)
body = re.search(r"<body>(.*?)</body>", html, re.S).group(1)
keep = "\n".join(l for l in head.splitlines() if "<title>" in l or "stylesheet" in l or 'name="description"' in l)
open(f"{ROOT}/build/artifact.html", "w", encoding="utf-8").write(keep + "\n" + body)
print("build/artifact.html", os.path.getsize(f"{ROOT}/build/artifact.html"), "bytes")
