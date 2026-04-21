<div align="center">

# 🔗 URL Shortener

**Lokaler URL-Shortener mit modernem Dark-Mode Dashboard**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![SQLite](https://img.shields.io/badge/SQLite-built--in-003b57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-7c3aed?style=for-the-badge)](LICENSE)

*Kein Account. Kein Cloud-Abo. Läuft komplett lokal.*

---

<!-- SCREENSHOT -->
<!-- Starte den Server, mach einen Screenshot vom Dashboard und ersetze den Platzhalter unten: -->
<!-- ![Dashboard Screenshot](docs/screenshot.png) -->

---

</div>

## Features

- **Web-Dashboard** — URLs kürzen, bearbeiten, löschen direkt im Browser
- **Klick-Charts** — 14-Tage Balkendiagramm pro Link (Chart.js)
- **QR-Codes** — sofort generiert, im Modal anzeigen oder als PNG herunterladen
- **Alias-Links** — eigene Kurzcodes wie `localhost:5000/github`
- **Ablaufdaten** — Links deaktivieren sich automatisch nach Datum
- **Bulk-Delete** — mehrere URLs auf einmal per Checkbox auswählen & löschen
- **Vorschau-Seite** — `/+<code>` zeigt das Ziel vor der Weiterleitung
- **CLI** — alles auch direkt im Terminal steuerbar
- **REST-API** — JSON-API für alle Operationen

---

## Schnellstart

**Doppelklick auf `start.bat`** — öffnet automatisch den Browser.

Oder manuell:

```bash
# Abhängigkeiten installieren (einmalig)
pip install -r requirements.txt

# Server starten → http://localhost:5000
python -m src.main serve
```

---

## Dashboard

| Bereich | Was du kannst |
|---|---|
| **Stats-Leiste** | Gesamt-URLs, Klicks gesamt, aktive Links auf einen Blick |
| **Kürzen-Form** | URL eingeben, optionalen Alias & Ablaufdatum setzen, Enter drücken |
| **Filter-Tabs** | Alle / Aktiv / Abgelaufen umschalten |
| **Suche** | Live-Suche über Code und Ziel-URL |
| **Tabelle** | Nach Code, URL, Klicks oder Datum sortieren (Spalte anklicken) |
| **Aktionen** | Kopieren · QR · Chart · Bearbeiten · Löschen pro Link |
| **Bulk-Select** | Checkboxen → mehrere Links gleichzeitig löschen |

**Keyboard Shortcuts:**

| Shortcut | Aktion |
|---|---|
| `Ctrl` + `K` | Fokus auf URL-Eingabe |
| `Escape` | Offenes Modal schließen |

---

## CLI

```bash
# URL kürzen
python -m src.main shorten https://github.com

# Mit Alias + Ablaufdatum
python -m src.main shorten https://github.com --alias gh --expires 2025-12-31

# Alle URLs anzeigen
python -m src.main list

# URL löschen
python -m src.main delete gh

# Statistiken (Top 3, Klicks gesamt)
python -m src.main stats

# QR-Code als PNG speichern → data/qr_gh.png
python -m src.main qr gh

# Server mit Optionen
python -m src.main serve --host 0.0.0.0 --port 8080 --debug
```

---

## REST-API

| Methode | Endpunkt | Beschreibung |
|---|---|---|
| `POST` | `/api/shorten` | URL kürzen |
| `GET` | `/api/urls` | Alle URLs als JSON |
| `PUT` | `/api/urls/<code>` | Ziel-URL eines Links ändern |
| `DELETE` | `/api/urls/<code>` | Link löschen |
| `GET` | `/api/qr/<code>` | QR-Code (base64 PNG) |
| `GET` | `/api/stats` | Gesamt-Statistiken |
| `GET` | `/api/clicks/<code>?days=14` | Klick-Verlauf |
| `GET` | `/<code>` | Weiterleitung |
| `GET` | `/+<code>` | Vorschau-Seite |

```bash
# URL kürzen
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com", "alias": "gh", "expires_at": "2025-12-31"}'

# Ziel-URL ändern
curl -X PUT http://localhost:5000/api/urls/gh \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/neues-ziel"}'

# Klick-Verlauf (14 Tage)
curl http://localhost:5000/api/clicks/gh?days=14

# Link löschen
curl -X DELETE http://localhost:5000/api/urls/gh
```

---

## Projektstruktur

```
001_url_shortener/
├── src/
│   ├── templates/
│   │   ├── index.html      # Dashboard (Chart.js, Toast-System, Dark UI)
│   │   └── preview.html    # Vorschau vor Weiterleitung
│   ├── app.py              # Flask-App & REST-API
│   ├── db.py               # SQLite-Layer (urls + click_log)
│   ├── main.py             # CLI (Click)
│   ├── models.py           # ShortURL, QR-Generator, Validator
│   └── utils.py            # Rich-Terminal-Ausgabe
├── data/
│   ├── urls.db             # SQLite-Datenbank (wird auto-erstellt)
│   └── qr_*.png            # Gespeicherte QR-Codes
├── tests/
│   └── test_main.py
├── requirements.txt
├── start.bat               # Doppelklick → Server + Browser
└── README.md
```

---

## Datenbank-Schema

```sql
CREATE TABLE urls (
    code        TEXT PRIMARY KEY,
    long_url    TEXT NOT NULL,
    alias       TEXT,
    clicks      INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now')),
    last_click  TEXT,
    expires_at  TEXT
);

CREATE TABLE click_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT NOT NULL,
    clicked_at  TEXT DEFAULT (datetime('now')),
    referrer    TEXT
);
```

---

## Abhängigkeiten

| Paket | Zweck |
|---|---|
| `flask` | Web-Framework & Routing |
| `click` | CLI-Framework |
| `rich` | Terminal-Ausgabe mit Farben & Tabellen |
| `qrcode[pil]` | QR-Code PNG Generierung |
| `python-dotenv` | `.env` Konfiguration |

```bash
pip install -r requirements.txt
```

---

## Tests

```bash
pytest tests/ -v
```

---

## Screenshot einfügen

1. Server starten (`start.bat` oder `python -m src.main serve`)
2. Screenshot vom Browser machen
3. Datei als `docs/screenshot.png` speichern
4. Diese Zeile in der README einkommentieren:

```md
![Dashboard Screenshot](docs/screenshot.png)
```

---

<div align="center">

MIT License · gebaut mit Python, Flask & Chart.js

</div>
