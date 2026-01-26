# Fehlerbehebung

Dieser Leitfaden hilft dir bei Problemen mit der Umgebungseinrichtung. Falls du auf skriptspezifische Probleme stößt, probier mal den Debug-Modus beim Ausführen der Skripte aus - er zeigt dir hilfreiche Fehlermeldungen und Hinweise.

## Umgebungseinrichtung

### AWS-Anmeldedaten konfigurieren

#### Problem: "Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**So behebst du das**:
```bash
# AWS-Anmeldedaten konfigurieren
aws configure
# Eingeben: Access Key ID, Secret Access Key, Region, Output format

# Konfiguration überprüfen
aws sts get-caller-identity
```

**Du kannst auch diese alternativen Methoden ausprobieren**:
- Umgebungsvariablen: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- AWS-Anmeldedatei: `~/.aws/credentials`
- IAM-Rollen (falls du auf EC2 oder Lambda läufst)

---

### Region konfigurieren

#### Problem: "Region not configured" oder "You must specify a region"

**So behebst du das**:
```bash
# Region in AWS CLI setzen
aws configure set region us-east-1

# Oder Umgebungsvariable verwenden
export AWS_DEFAULT_REGION=us-east-1

# Region überprüfen
aws configure get region
```

**Funktioniert mit diesen Regionen**: Jede AWS-Region, in der IoT Core verfügbar ist

---

### Python-Abhängigkeiten

#### Problem: "No module named 'colorama'" oder ähnliche Import-Fehler
```
ModuleNotFoundError: No module named 'colorama'
```

**So behebst du das**:
```bash
# Alle Abhängigkeiten installieren
pip install -r requirements.txt

# Oder einzeln installieren
pip install boto3>=1.40.27 colorama>=0.4.4 requests>=2.25.1
```

**So kannst du deine Installation überprüfen**:
```bash
python -c "import boto3, colorama, requests; print('All dependencies installed')"
```

---

### IAM-Berechtigungen

#### Problem: "Access Denied" oder "User is not authorized" Fehler
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**So behebst du das**: Stell sicher, dass dein AWS IAM-Benutzer oder deine Rolle die nötigen Berechtigungen hat:

**Was du brauchst - IAM-Aktionen**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iot:*",
                "iot-data:*",
                "iot-jobs-data:*",
                "s3:GetObject",
                "s3:PutObject",
                "s3:CreateBucket",
                "s3:DeleteBucket",
                "s3:ListBucket",
                "s3:PutBucketTagging",
                "iam:GetRole",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:PassRole",
                "iam:TagRole",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

**Kurzer Hinweis**: Für Produktionsumgebungen ist es eine gute Idee, dem Prinzip der minimalen Rechte zu folgen und Ressourcen nach Bedarf einzuschränken.

---

## Hilfe bekommen

### Skriptspezifische Probleme

Falls du beim Ausführen von Skripten auf Probleme stößt, hier ein paar hilfreiche Tipps:

1. **Debug-Modus aktivieren** - Er zeigt dir detaillierte API-Aufrufe und Antworten
   ```
   🔧 Enable debug mode? [y/N]: y
   ```

2. **Fehlermeldungen lesen** - Die Skripte geben dir hilfreiche kontextbezogene Hinweise

3. **Lernpausen beachten** - Sie erklären dir Konzepte und Anforderungen während der Ausführung

4. **Voraussetzungen prüfen** - Die meisten Skripte benötigen zuerst `provision_script.py`

### So sieht ein typischer Ablauf aus

```bash
# 1. Umgebung einrichten (nur einmal)
aws configure
export AWS_DEFAULT_REGION=us-east-1
pip install -r requirements.txt

# 2. Infrastruktur erstellen (zuerst ausführen)
python scripts/provision_script.py

# 3. Andere Skripte nach Bedarf ausführen
python scripts/manage_packages.py
python scripts/create_job.py
# usw.

# 4. Aufräumen, wenn du fertig bist
python scripts/cleanup_script.py
```

### Weitere hilfreiche Ressourcen

- **README.md** - Projektübersicht und Schnellstart-Anleitung
- **Skript-i18n-Nachrichten** - Hilfreiche Hinweise in deiner Sprache
- **Lernpausen** - Lerne während der Skriptausführung
- **AWS IoT Dokumentation** - https://docs.aws.amazon.com/iot/

