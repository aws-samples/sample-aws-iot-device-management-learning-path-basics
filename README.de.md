# AWS IoT Device Management - Lernpfad - Grundlagen

## 🌍 Verfügbare Sprachen | Available Languages | Idiomas Disponibles | 利用可能な言語 | 사용 가능한 언어 | Idiomas Disponíveis | 可用语言

| Sprache | README |
|----------|---------|
| 🇺🇸 English | [README.md](README.md) |
| 🇪🇸 Español | [README.es.md](README.es.md) |
| 🇯🇵 日本語 | [README.ja.md](README.ja.md) |
| 🇰🇷 한국어 | [README.ko.md](README.ko.md) |
| 🇧🇷 Português | [README.pt.md](README.pt.md) |
| 🇨🇳 中文 | [README.zh.md](README.zh.md) |
| 🇩🇪 Deutsch | [README.de.md](README.de.md) |
| 🇮🇹 Italiano | [README.it.md](README.it.md) |
| 🇫🇷 Français | [README.fr.md](README.fr.md) |

---

Eine umfassende Demonstration der AWS IoT Device Management-Funktionen, einschließlich Gerätebereitstellung, Over-the-Air (OTA) Updates, Job-Management und Flottenbetrieb. Dieses Projekt verwendet moderne Python-Skripte mit nativer AWS SDK (boto3) Integration, um dir zu helfen, diese Konzepte praktisch zu erlernen.

## 👥 Zielgruppe

**Hauptzielgruppe:** IoT-Entwickler, Solution Architects und DevOps-Engineers, die mit AWS IoT-Geräteflotten arbeiten

**Voraussetzungen:** Fortgeschrittene AWS-Kenntnisse, AWS IoT Core-Grundlagen, Python-Grundlagen und Kommandozeilennutzung

**Lernniveau:** Associate-Level mit einem praktischen Ansatz für Geräteverwaltung im großen Maßstab

## 🎯 Lernziele

- **Geräte-Lebenszyklus-Management**: IoT-Geräte mit passenden Thing-Typen und Attributen bereitstellen
- **Flottenorganisation**: Statische und dynamische Thing-Gruppen für die Geräteverwaltung erstellen
- **OTA-Updates**: Firmware-Updates mit AWS IoT Jobs und Amazon S3-Integration implementieren
- **Paketverwaltung**: Mehrere Firmware-Versionen mit automatisierten Shadow-Updates verwalten
- **Job-Ausführung**: Realistisches Geräteverhalten während Firmware-Updates simulieren
- **Versionskontrolle**: Geräte auf frühere Firmware-Versionen zurücksetzen
- **Remote-Befehle**: Echtzeitbefehle an Geräte mit AWS IoT Commands senden
- **Massenregistrierung**: Hunderte oder Tausende von Geräten effizient mit Bereitstellung im Fertigungsmaßstab registrieren
- **Ressourcen-Bereinigung**: AWS-Ressourcen ordnungsgemäß verwalten, um unnötige Kosten zu vermeiden



## 📋 Voraussetzungen

- **AWS-Konto** mit Berechtigungen für AWS IoT, Amazon S3 und AWS Identity and Access Management (IAM)
- **AWS-Anmeldedaten** konfiguriert (du kannst `aws configure`, Umgebungsvariablen oder IAM-Rollen verwenden)
- **Python 3.10+** mit pip und den Python-Bibliotheken boto3, colorama und requests (siehe requirements.txt-Datei)
- **Git** zum Klonen des Repositorys

## 💰 Kostenanalyse

**Dieses Projekt erstellt echte AWS-Ressourcen, die Kosten verursachen. Hier ist, was du erwarten kannst:**

| Service | Nutzung | Geschätzte Kosten (USD) |
|---------|-------|---------------------|
| **AWS IoT Core** | ~1.000 Nachrichten, 100-10.000 Geräte | $0.08 - $0.80 |
| **AWS IoT Device Shadow** | ~200-2.000 Shadow-Operationen | $0.10 - $1.00 |
| **AWS IoT Jobs** | ~10-100 Job-Ausführungen | $0.01 - $0.10 |
| **AWS IoT Commands** | ~10-50 Befehlsausführungen | $0.01 - $0.05 |
| **Amazon S3** | Speicherung + Anfragen für Firmware | $0.05 - $0.25 |
| **AWS IoT Fleet Indexing** | Geräteabfragen und Indexierung | $0.02 - $0.20 |
| **AWS IoT Device Management Software Package Catalog** | Paketoperationen | $0.01 - $0.05 |
| **AWS IoT Device Management Bulk Registration** | Massengerätebereitstellung | $0.05 - $0.50 |
| **AWS Identity and Access Management (IAM)** | Rollen-/Richtlinienverwaltung | $0.00 |
| **Geschätzte Gesamtkosten** | **Komplette Demo-Sitzung** | **$0.33 - $2.95** |

**Kostenfaktoren:**
- Geräteanzahl (100-10.000 konfigurierbar)
- Job-Ausführungshäufigkeit
- Shadow-Update-Operationen
- Amazon S3-Speicherdauer

**Kostenmanagement:**
- ✅ Bereinigungsskript entfernt alle Ressourcen
- ✅ Kurzlebige Demo-Ressourcen
- ✅ Konfigurierbarer Umfang (fang klein an)
- ⚠️ **Denk daran, das Bereinigungsskript auszuführen, wenn du fertig bist**

**📊 Kosten überwachen:** [AWS Billing Dashboard](https://console.aws.amazon.com/billing/)

## 🚀 Schnellstart

```bash
# 1. Klonen und einrichten
git clone https://github.com/aws-samples/sample-aws-iot-device-management-learning-path-basics.git
cd sample-aws-iot-device-management-learning-path-basics
python3 -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. AWS konfigurieren
aws configure

# 3. Kompletter Workflow (wir empfehlen diese Reihenfolge)
python scripts/provision_script.py        # Infrastruktur mit Tagging erstellen
python scripts/manage_dynamic_groups.py   # Gerätegruppen erstellen
python scripts/manage_packages.py         # Firmware-Pakete verwalten
python scripts/create_job.py              # Firmware-Updates bereitstellen
python scripts/simulate_job_execution.py  # Geräte-Updates simulieren
python scripts/explore_jobs.py            # Job-Fortschritt überwachen
python scripts/manage_commands.py         # Echtzeitbefehle an Geräte senden
python scripts/manage_bulk_provisioning.py # Massengeräteregistrierung (Fertigungsmaßstab)
python scripts/cleanup_script.py          # Sichere Bereinigung mit Ressourcenidentifikation
```

## 📚 Verfügbare Skripte

| Skript | Zweck | Hauptfunktionen |
|--------|---------|-------------|
| **provision_script.py** | Komplette Infrastruktur-Einrichtung | Erstellt Geräte, Gruppen, Pakete, Amazon S3-Speicher |
| **manage_dynamic_groups.py** | Dynamische Gerätegruppen verwalten | Erstellen, auflisten, löschen mit Fleet Indexing-Validierung |
| **manage_packages.py** | Umfassende Paketverwaltung | Pakete/Versionen erstellen, Amazon S3-Integration, Geräteverfolgung mit individuellem Rücksetzstatus |
| **create_job.py** | OTA-Update-Jobs erstellen | Multi-Gruppen-Targeting, vorsignierte URLs |
| **simulate_job_execution.py** | Geräte-Updates simulieren | Echte Amazon S3-Downloads, sichtbare Planvorbereitung, Fortschrittsverfolgung pro Gerät |
| **explore_jobs.py** | Jobs überwachen und verwalten | Interaktive Job-Erkundung, Abbruch, Löschung und Analysen |
| **manage_commands.py** | Echtzeitbefehle an Geräte senden | Template-Verwaltung, Befehlsausführung, Statusüberwachung, Verlaufsverfolgung |
| **manage_bulk_provisioning.py** | Massengeräteregistrierung | Gerätebereitstellung im Fertigungsmaßstab, Zertifikatsgenerierung, Aufgabenüberwachung |
| **cleanup_script.py** | AWS-Ressourcen entfernen | Selektive Bereinigung, Kostenmanagement |

## ⚙️ Konfiguration

**Umgebungsvariablen** (optional):
```bash
export AWS_DEFAULT_REGION=us-east-1
export AWS_IOT_LANG=de                    # Standardsprache festlegen (en, es, fr, etc.)
```

**Skript-Funktionen**:
- **Natives AWS SDK**: Verwendet boto3 für bessere Leistung und Zuverlässigkeit
- **Mehrsprachige Unterstützung**: Interaktive Sprachauswahl mit Fallback auf Englisch
- **Debug-Modus**: Zeigt alle AWS API-Aufrufe und -Antworten
- **Parallele Verarbeitung**: Gleichzeitige Operationen, wenn nicht im Debug-Modus
- **Rate Limiting**: Automatische Einhaltung der AWS API-Drosselung
- **Fortschrittsverfolgung**: Echtzeit-Operationsstatus
- **Ressourcen-Tagging**: Automatische Workshop-Tags für sichere Bereinigung
- **Konfigurierbare Benennung**: Anpassbare Gerätebenennungsmuster

### Ressourcen-Tagging

Alle Workshop-Skripte taggen automatisch erstellte Ressourcen mit `workshop=learning-aws-iot-dm-basics` zur sicheren Identifikation während der Bereinigung. Dies stellt sicher, dass nur vom Workshop erstellte Ressourcen gelöscht werden.

**Getaggte Ressourcen**:
- IoT Thing Types
- IoT Thing Groups (statisch und dynamisch)
- IoT Software Packages
- AWS IoT Jobs
- Amazon S3 Buckets
- AWS Identity and Access Management (IAM) Rollen

**Nicht getaggte Ressourcen** (durch Benennungsmuster identifiziert):
- IoT Things (verwenden Benennungskonventionen)
- Zertifikate (durch Zuordnung identifiziert)
- Thing Shadows (durch Zuordnung identifiziert)

### Gerätebenennungskonfiguration

Passe Gerätebenennungsmuster mit dem Parameter `--things-prefix` an:

```bash
# Standardbenennung: Vehicle-VIN-001, Vehicle-VIN-002, etc.
python scripts/provision_script.py

# Benutzerdefiniertes Präfix: Fleet-Device-001, Fleet-Device-002, etc.
python scripts/provision_script.py --things-prefix "Fleet-Device-"

# Benutzerdefiniertes Präfix für Bereinigung (muss mit Bereitstellungspräfix übereinstimmen)
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"
```

**Präfix-Anforderungen**:
- Verwende alphanumerische Zeichen, Bindestriche, Unterstriche und Doppelpunkte
- Halte es unter 20 Zeichen
- Sequentielle Nummern werden automatisch mit Nullen aufgefüllt (001-999)

## 🌍 Internationalisierungsunterstützung

Alle Skripte unterstützen mehrere Sprachen mit automatischer Spracherkennung und interaktiver Auswahl.

**Sprachauswahl**:
- **Interaktiv**: Skripte fordern zur Sprachauswahl beim ersten Ausführen auf
- **Umgebungsvariable**: Setze `AWS_IOT_LANG=de`, um die Sprachauswahl zu überspringen
- **Fallback**: Fällt automatisch auf Englisch zurück bei fehlenden Übersetzungen

**Unterstützte Sprachen**:
- **English (en)**: Vollständige Übersetzungen ✅
- **Spanish (es)**: Bereit für Übersetzungen
- **Japanese (ja)**: Bereit für Übersetzungen  
- **Chinese (zh-CN)**: Bereit für Übersetzungen
- **Portuguese (pt-BR)**: Bereit für Übersetzungen
- **Korean (ko)**: Bereit für Übersetzungen

**Verwendungsbeispiele**:
```bash
# Sprache über Umgebungsvariable setzen (empfohlen für Automatisierung)
export AWS_IOT_LANG=de
python scripts/provision_script.py

# Alternative Sprachcodes werden unterstützt
export AWS_IOT_LANG=german     # oder "de", "deutsch"
export AWS_IOT_LANG=spanish    # oder "es", "español"
export AWS_IOT_LANG=japanese   # oder "ja", "日本語", "jp"
export AWS_IOT_LANG=chinese    # oder "zh-cn", "中文", "zh"
export AWS_IOT_LANG=portuguese # oder "pt", "pt-br", "português"
export AWS_IOT_LANG=korean     # oder "ko", "한국어", "kr"

# Interaktive Sprachauswahl (Standardverhalten)
python scripts/manage_packages.py
# Ausgabe: 🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择 / Seleção de Idioma / 언어 선택
#         1. English
#         2. Español (Spanish)
#         3. 日本語 (Japanese)
#         4. 中文 (Chinese)
#         5. Português (Portuguese)
#         6. 한국어 (Korean)
#         Select language (1-6): 

# Alle benutzerseitigen Texte erscheinen in der gewählten Sprache
```

**Nachrichtenkategorien**:
- **UI-Elemente**: Titel, Überschriften, Trennzeichen
- **Benutzereingaben**: Eingabeanforderungen, Bestätigungen
- **Statusmeldungen**: Fortschrittsaktualisierungen, Erfolgs-/Fehlermeldungen
- **Fehlermeldungen**: Detaillierte Fehlerbeschreibungen und Fehlerbehebung
- **Debug-Ausgabe**: API-Aufrufsinformationen und -Antworten
- **Lerninhalte**: Lehrreiche Momente und Erklärungen

## 📖 Verwendungsbeispiele

**Kompletter Workflow** (wir empfehlen diese Reihenfolge):
```bash
python scripts/provision_script.py        # 1. Infrastruktur erstellen
python scripts/manage_dynamic_groups.py   # 2. Gerätegruppen erstellen
python scripts/manage_packages.py         # 3. Firmware-Pakete verwalten
python scripts/create_job.py              # 4. Firmware-Updates bereitstellen
python scripts/simulate_job_execution.py  # 5. Geräte-Updates simulieren
python scripts/explore_jobs.py            # 6. Job-Fortschritt überwachen
python scripts/manage_commands.py         # 7. Echtzeitbefehle an Geräte senden
python scripts/cleanup_script.py          # 8. Ressourcen bereinigen
```

**Einzelne Operationen**:
```bash
python scripts/manage_packages.py         # Paket- und Versionsverwaltung
python scripts/manage_dynamic_groups.py   # Dynamische Gruppenoperationen
```

## 🛠️ Fehlerbehebung

**Häufige Probleme**:
- **Anmeldedaten**: Du kannst AWS-Anmeldedaten über `aws configure`, Umgebungsvariablen oder IAM-Rollen konfigurieren
- **Berechtigungen**: Stelle sicher, dass dein IAM-Benutzer AWS IoT-, Amazon S3- und IAM-Berechtigungen hat
- **Rate Limits**: Keine Sorge - Skripte handhaben dies automatisch mit intelligenter Drosselung
- **Netzwerk**: Stelle sicher, dass du Verbindung zu AWS APIs hast

**Debug-Modus**: Du kannst dies in jedem Skript für detaillierte Fehlerbehebung aktivieren
```bash
🔧 Debug-Modus aktivieren (alle API-Aufrufe und -Antworten anzeigen)? [y/N]: y
```

> 📖 **Detaillierte Fehlerbehebung**: Siehe [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) für umfassende Lösungen.

## 🧹 Wichtig: Ressourcen-Bereinigung

**Denk daran, die Bereinigung auszuführen, wenn du fertig bist, um laufende Kosten zu vermeiden:**
```bash
python scripts/cleanup_script.py
# Wähle Option 1: ALLE Ressourcen
# Tippe: DELETE
```

### Sichere Bereinigungsfunktionen

Das Bereinigungsskript verwendet mehrere Identifikationsmethoden, um sicherzustellen, dass nur Workshop-Ressourcen gelöscht werden:

1. **Tag-basierte Identifikation** (Primär): Prüft auf `workshop=learning-aws-iot-dm-basics` Tag
2. **Benennungsmuster-Abgleich** (Sekundär): Gleicht bekannte Workshop-Benennungskonventionen ab
3. **Zuordnungsbasiert** (Tertiär): Identifiziert Ressourcen, die mit Workshop-Ressourcen verbunden sind

**Bereinigungsoptionen**:
```bash
# Standard-Bereinigung (interaktiv)
python scripts/cleanup_script.py

# Dry-Run-Modus (Vorschau ohne Löschen)
python scripts/cleanup_script.py --dry-run

# Benutzerdefiniertes Gerätepräfix (muss mit Bereitstellungspräfix übereinstimmen)
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"

# Dry-Run mit benutzerdefiniertem Präfix
python scripts/cleanup_script.py --dry-run --things-prefix "Fleet-Device-"
```

**Was die Bereinigung entfernt:**
- Alle AWS IoT-Geräte und -Gruppen (mit Workshop-Tags oder passenden Benennungsmustern)
- Amazon S3-Buckets und Firmware-Dateien (getaggt)
- AWS IoT Software Packages (getaggt)
- AWS IoT Command Templates (getaggt)
- IAM-Rollen und -Richtlinien (getaggt)
- Fleet Indexing-Konfiguration
- Zugehörige Zertifikate und Shadows

**Sicherheitsfunktionen**:
- Nicht-Workshop-Ressourcen werden automatisch übersprungen
- Du siehst eine detaillierte Zusammenfassung der gelöschten und übersprungenen Ressourcen
- Debug-Modus zeigt die Identifikationsmethode für jede Ressource
- Dry-Run-Modus lässt dich vor dem tatsächlichen Löschen eine Vorschau sehen

## 📁 Projektstruktur

```
sample-aws-iot-device-management-learning-path-basics/
├── scripts/                          # Benutzerfreundliche ausführbare Skripte
│   ├── provision_script.py          # IoT-Ressourcen bereitstellen
│   ├── cleanup_script.py            # Workshop-Ressourcen bereinigen
│   ├── manage_packages.py           # Paketverwaltung
│   ├── manage_dynamic_groups.py     # Dynamische Gruppenoperationen
│   ├── create_job.py                # OTA-Jobs erstellen
│   ├── simulate_job_execution.py    # Geräte-Updates simulieren
│   ├── explore_jobs.py              # Job-Fortschritt überwachen
│   └── manage_commands.py           # Echtzeitbefehle senden
├── iot_helpers/                     # Internes Hilfspaket
│   ├── cleanup/                     # Bereinigungsoperationsmodule
│   │   ├── reporter.py             # Bereinigungsberichterstattung
│   │   ├── deletion_engine.py      # Ressourcenlöschung
│   │   └── resource_identifier.py  # Ressourcenidentifikation
│   └── utils/                       # Utility-Module
│       ├── naming_conventions.py   # Benennungsmuster
│       ├── resource_tagger.py      # Ressourcen-Tagging
│       └── dependency_handler.py   # Abhängigkeitsverwaltung
├── i18n/                            # Internationalisierung
│   ├── common.json                 # Gemeinsame Nachrichten
│   ├── loader.py                   # Nachrichtenladung
│   ├── language_selector.py        # Sprachauswahl
│   └── {language_code}/            # Sprachspezifische Nachrichten
├── docs/                            # Dokumentation
│   └── TROUBLESHOOTING.md          # Fehlerbehebungsleitfaden
├── tests/                           # Testdateien
└── requirements.txt                 # Python-Abhängigkeiten
```

## 🔧 Entwicklerleitfaden: Neue Sprachen hinzufügen

**Nachrichtendateistruktur**:
```
i18n/
├── common.json                    # Gemeinsame Nachrichten über alle Skripte hinweg
├── loader.py                      # Nachrichtenlade-Utility
├── language_selector.py           # Sprachauswahl-Schnittstelle
└── {language_code}/               # Sprachspezifisches Verzeichnis
    ├── provision_script.json     # Skriptspezifische Nachrichten
    ├── manage_dynamic_groups.json
    ├── manage_packages.json
    ├── create_job.json
    ├── simulate_job_execution.json
    ├── explore_jobs.json
    └── cleanup_script.json
```

**Eine neue Sprache hinzufügen**:

1. **Sprachverzeichnis erstellen**:
   ```bash
   mkdir i18n/{language_code}  # z.B. i18n/es für Spanisch
   ```

2. **Englische Vorlagen kopieren**:
   ```bash
   cp i18n/en/*.json i18n/{language_code}/
   ```

3. **Nachrichtendateien übersetzen**:
   Jede JSON-Datei enthält kategorisierte Nachrichten:
   ```json
   {
     "title": "📦 AWS IoT Software Package Manager (Boto3)",
     "separator": "============================================",
     "prompts": {
       "debug_mode": "🔧 Debug-Modus aktivieren? [y/N]: ",
       "operation_choice": "Wahl eingeben [1-11]: ",
       "continue_operation": "Fortfahren? [Y/n]: "
     },
     "status": {
       "debug_enabled": "✅ Debug-Modus aktiviert",
       "package_created": "✅ Paket erfolgreich erstellt",
       "clients_initialized": "🔍 DEBUG: Client-Konfiguration:"
     },
     "errors": {
       "invalid_choice": "❌ Ungültige Wahl. Bitte 1-11 eingeben",
       "package_not_found": "❌ Paket '{}' nicht gefunden",
       "api_error": "❌ Fehler in {} {}: {}"
     },
     "debug": {
       "api_call": "📤 API-Aufruf: {}",
       "api_response": "📤 API-Antwort:",
       "debug_operation": "🔍 DEBUG: {}: {}"
     },
     "ui": {
       "operation_menu": "🎯 Operation auswählen:",
       "create_package": "1. Software-Paket erstellen",
       "goodbye": "👋 Danke, dass du den Package Manager verwendet hast!"
     },
     "learning": {
       "package_management_title": "Software-Paketverwaltung",
       "package_management_description": "Lerninhalt..."
     }
   }
   ```

4. **Sprachauswahl aktualisieren** (wenn neue Sprache hinzugefügt wird):
   Füge deine Sprache zu `i18n/language_selector.py` hinzu:
   ```python
   LANGUAGE_SELECTION = {
       "options": [
           "1. English",
           "2. Español (Spanish)",
           "3. Dein Sprachname",  # Neue Option hinzufügen
           # ... vorhandene Sprachen
       ],
   }
   
   LANGUAGE_CODES = {
       "1": "en", 
       "2": "es", 
       "3": "dein_code",  # Neuen Sprachcode hinzufügen
       # ... vorhandene Zuordnungen
   }
   ```

5. **Übersetzung testen**:
   ```bash
   export AWS_IOT_LANG={language_code}
   python scripts/provision_script.py
   ```

**Übersetzungsrichtlinien**:
- **Formatierung beibehalten**: Behalte Emojis, Farben und Sonderzeichen wie sie sind
- **Platzhalter beibehalten**: Behalte `{}`-Platzhalter für dynamischen Inhalt
- **Technische Begriffe**: Behalte AWS-Servicenamen auf Englisch
- **Kulturelle Anpassung**: Fühle dich frei, Beispiele und Referenzen angemessen anzupassen
- **Konsistenz**: Verwende konsistente Terminologie über alle Dateien hinweg

**Nachrichtenschlüsselmuster**:
- `title`: Haupttitel des Skripts
- `separator`: Visuelle Trennzeichen und Teiler  
- `prompts.*`: Benutzereingabeanforderungen und Bestätigungen
- `status.*`: Fortschrittsaktualisierungen und Operationsergebnisse
- `errors.*`: Fehlermeldungen und Warnungen
- `debug.*`: Debug-Ausgabe und API-Informationen
- `ui.*`: Benutzeroberflächenelemente (Menüs, Labels, Buttons)
- `results.*`: Operationsergebnisse und Datenanzeige
- `learning.*`: Lerninhalt und Erklärungen
- `warnings.*`: Warnmeldungen und wichtige Hinweise
- `explanations.*`: Zusätzlicher Kontext und Hilfetext

**Deine Übersetzung testen**:
```bash
# Bestimmtes Skript mit deiner Sprache testen
export AWS_IOT_LANG=dein_sprachcode
python scripts/manage_packages.py

# Fallback-Verhalten testen (nicht existierende Sprache verwenden)
export AWS_IOT_LANG=xx
python scripts/provision_script.py  # Sollte auf Englisch zurückfallen
```

## 📚 Dokumentation

- **[Fehlerbehebung](docs/TROUBLESHOOTING.md)** - Häufige Probleme und Lösungen

## 📄 Lizenz

MIT No Attribution License - siehe [LICENSE](LICENSE)-Datei für Details.

## 🏷️ Tags

`aws` `aws-iot` `device-management` `ota-updates` `fleet-management` `python` `demo` `iot` 
