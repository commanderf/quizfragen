#!/usr/bin/env python3
"""Baut site/ aus app/ für GitHub Pages.

Aktuell OHNE Service-Worker/PWA: reine statische Seite, immer aktuell
online geladen. Der Update-Banner (update.js + version.json) bleibt.
Die PWA-Teile (sw.js, pwa.js, Manifest, Icons, pwa-bar) sind entfernt
und können hier später kontrolliert wieder eingebaut werden.
"""
import hashlib, json, pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parent
APP = ROOT / "app"
SITE = ROOT / "site"

def build():
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()

    for name in ["index.html", "styles.css", "app.js", "questions.js", "update.js", "version.json"]:
        shutil.copy2(APP / name, SITE / name)
    (SITE / '.nojekyll').touch()

    digest = hashlib.sha256(''.join(
        f"{p.name}{hashlib.sha256(p.read_bytes()).hexdigest()}"
        for p in sorted(SITE.rglob('*')) if p.is_file()
    ).encode()).hexdigest()[:16]
    print("site/ gebaut (ohne PWA). Build-Version:", digest)

if __name__ == "__main__":
    build()
