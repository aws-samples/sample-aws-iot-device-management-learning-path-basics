# Guida alla Risoluzione dei Problemi

Questa guida ti aiuta a risolvere i problemi di configurazione dell'ambiente. Se incontri problemi specifici con gli script, prova ad abilitare la modalità debug quando esegui gli script - ti fornirà messaggi di errore utili e indicazioni lungo il percorso.

## Configurazione dell'Ambiente

### Configurazione delle Credenziali AWS

#### Problema: "Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**Ecco come risolverlo**:
```bash
# Configura le credenziali AWS
aws configure
# Inserisci: Access Key ID, Secret Access Key, Region, Output format

# Verifica la configurazione
aws sts get-caller-identity
```

**Puoi anche provare questi metodi alternativi**:
- Variabili d'ambiente: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- File delle credenziali AWS: `~/.aws/credentials`
- Ruoli IAM (se stai eseguendo su EC2 o Lambda)

---

### Configurazione della Regione

#### Problema: "Region not configured" o "You must specify a region"

**Ecco come risolverlo**:
```bash
# Imposta la regione nella AWS CLI
aws configure set region us-east-1

# Oppure usa una variabile d'ambiente
export AWS_DEFAULT_REGION=us-east-1

# Verifica la regione
aws configure get region
```

**Funziona con queste regioni**: Qualsiasi regione AWS dove IoT Core è disponibile

---

### Dipendenze Python

#### Problema: "No module named 'colorama'" o errori di importazione simili
```
ModuleNotFoundError: No module named 'colorama'
```

**Ecco come risolverlo**:
```bash
# Installa tutte le dipendenze
pip install -r requirements.txt

# Oppure installa individualmente
pip install boto3>=1.40.27 colorama>=0.4.4 requests>=2.25.1
```

**Puoi verificare la tua installazione così**:
```bash
python -c "import boto3, colorama, requests; print('All dependencies installed')"
```

---

### Permessi IAM

#### Problema: Errori "Access Denied" o "User is not authorized"
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**Ecco come risolverlo**: Assicurati che il tuo utente o ruolo IAM AWS abbia i permessi necessari:

**Quello che ti servirà - Azioni IAM**:
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

**Nota veloce**: Per gli ambienti di produzione, è una buona idea seguire il principio del privilegio minimo e limitare le risorse secondo necessità.

---

## Ottenere Aiuto

### Problemi Specifici degli Script

Se incontri problemi durante l'esecuzione degli script, ecco alcuni suggerimenti utili:

1. **Abilita la modalità debug** - Ti mostrerà le chiamate API dettagliate e le risposte
   ```
   🔧 Enable debug mode? [y/N]: y
   ```

2. **Leggi i messaggi di errore** - Gli script forniscono indicazioni contestuali utili

3. **Controlla le pause educative** - Spiegano concetti e requisiti mentre procedi

4. **Controlla i prerequisiti** - La maggior parte degli script richiede l'esecuzione prima di `provision_script.py`

### Ecco un flusso di lavoro tipico

```bash
# 1. Configura il tuo ambiente (solo una volta)
aws configure
export AWS_DEFAULT_REGION=us-east-1
pip install -r requirements.txt

# 2. Crea la tua infrastruttura (esegui questo per primo)
python scripts/provision_script.py

# 3. Esegui altri script secondo necessità
python scripts/manage_packages.py
python scripts/create_job.py
# ecc.

# 4. Pulisci quando hai finito
python scripts/cleanup_script.py
```

### Altre risorse utili

- **README.md** - Panoramica del progetto e guida rapida
- **Messaggi i18n degli script** - Indicazioni utili nella tua lingua
- **Pause educative** - Impara mentre procedi durante l'esecuzione degli script
- **Documentazione AWS IoT** - https://docs.aws.amazon.com/iot/

