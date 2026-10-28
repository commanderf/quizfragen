# Zeitreise – Das Quiz

Nostalgisches Multiple-Choice-Quiz mit Fragen aus den 70ern, 80ern, 90ern und 2000ern – auf Deutsch, ohne Anmeldung, ohne Tracking. Spielstand und Statistik bleiben lokal im Browser (localStorage).

## Im Browser spielen

Die aktuelle Version läuft auf GitHub Pages:

- **https://commanderf.github.io/quizfragen/** (falls das Repo umbenannt wird, ändert sich die URL entsprechend)

Die Seite ist als PWA installierbar ("Als App installieren" links im Kopfbereich) und danach offline spielbar. Ein „Update laden"-Button bzw. ein orangefarbenes Update-Banner erscheint, wenn eine neuere Version verfügbar ist – dabei bleiben Spielstände und Statistik erhalten.

## Runden anpassen

Vor jeder Runde wählen:

- **Jahrzehnt:** 70er, 80er, 90er, 00er oder alle zusammen
- **Kategorien:** Musik, Film & Fernsehen, Alltag & Technik, Zeitgeschehen & Sport
- **Anzahl:** 10–40 Fragen
- **Schwierigkeit:** leicht / mittel / schwer

Eine nicht beendete Runde wird automatisch zwischengespeichert – auf der Startseite lässt sie sich per „Fortsetzen" wieder öffnen.

## Struktur

- `app/` – Quellcode (Questions-Datenbank, App-Logik, Update-Banner)
- `site/` – Für GitHub Pages gebaute Version (inkl. PWA: Service Worker, Manifest, Icons); wird mit `python3 build-site.py` aus `app/` neu erzeugt
- `.github/workflows/deploy.yml` – Baut & published bei jedem Push auf `main` nach GitHub Pages
- `quality-update.py` – Historischer Qualitäts-Patch (nur für den Legacy-Archiv-Build, wird bei vorhandenem `site/` übersprungen)

## Neu bauen / Fragen ergänzen

1. Fragen in `app/questions.js` ergänzen (Schema siehe Datei: `id`, `decade`, `category`, `difficulty`, `question`, `answers`, `correct`, `explanation`, `source`)
2. Version bumpen: Version in `app/update.js` **und** `app/version.json` anheben (löst das Update-Banner bei Nutzern aus)
3. `python3 build-site.py` ausführen
4. Committen und pushen – der Workflow deployed automatisch

## Lokal testen

```bash
cd app
python3 -m http.server 8000 --bind 0.0.0.0
```

Dann http://<host-ip>:8000/ öffnen (nicht localhost, wenn du von einem anderen Gerät testest).

---

Basierend auf dem Original-Quiz „Zeitreise – Das 70er & 80er Quiz" (siehe `6751629b.tar`).
