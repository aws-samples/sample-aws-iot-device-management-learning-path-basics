# AWS IoT Device Management - Percorso di Apprendimento - Fondamenti

## 🌍 Lingue Disponibili | Available Languages | Idiomas Disponibles | 利用可能な言語 | 사용 가능한 언어 | Idiomas Disponíveis | 可用语言

| Lingua | README |
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

Una dimostrazione completa delle funzionalità di AWS IoT Device Management, inclusi provisioning dei dispositivi, aggiornamenti over-the-air (OTA), gestione dei job e operazioni sulla flotta. Questo progetto usa script Python moderni con integrazione nativa dell'AWS SDK (boto3) per aiutarti a imparare questi concetti in modo pratico.

## 👥 Pubblico di Riferimento

**Pubblico Principale:** Sviluppatori IoT, solution architect e ingegneri DevOps che lavorano con flotte di dispositivi AWS IoT

**Prerequisiti:** Conoscenza intermedia di AWS, fondamenti di AWS IoT Core, fondamenti di Python e uso della riga di comando

**Livello di Apprendimento:** Livello associate con un approccio pratico alla gestione dei dispositivi su larga scala

## 🎯 Obiettivi di Apprendimento

- **Gestione del Ciclo di Vita dei Dispositivi**: Effettua il provisioning dei dispositivi IoT con i tipi e gli attributi appropriati
- **Organizzazione della Flotta**: Crea gruppi di dispositivi statici e dinamici per la gestione
- **Aggiornamenti OTA**: Implementa aggiornamenti firmware usando AWS IoT Jobs con integrazione Amazon S3
- **Gestione dei Pacchetti**: Gestisci più versioni di firmware con aggiornamenti automatici delle shadow
- **Esecuzione dei Job**: Simula comportamenti realistici dei dispositivi durante gli aggiornamenti firmware
- **Controllo delle Versioni**: Ripristina i dispositivi alle versioni firmware precedenti
- **Comandi Remoti**: Invia comandi in tempo reale ai dispositivi usando AWS IoT Commands
- **Registrazione in Blocco**: Registra centinaia o migliaia di dispositivi in modo efficiente usando il provisioning su scala produttiva
- **Pulizia delle Risorse**: Gestisci correttamente le risorse AWS per evitare costi non necessari



## 📋 Prerequisiti

- **Account AWS** con permessi per AWS IoT, Amazon S3 e AWS Identity and Access Management (IAM)
- **Credenziali AWS** configurate (puoi usare `aws configure`, variabili d'ambiente o ruoli IAM)
- **Python 3.10+** con pip e le librerie Python boto3, colorama e requests (controlla il file requirements.txt)
- **Git** per clonare il repository

## 💰 Analisi dei Costi

**Questo progetto crea risorse AWS reali che comporteranno addebiti. Ecco cosa aspettarti:**

| Servizio | Utilizzo | Costo Stimato (USD) |
|---------|-------|---------------------|
| **AWS IoT Core** | ~1.000 messaggi, 100-10.000 dispositivi | $0.08 - $0.80 |
| **AWS IoT Device Shadow** | ~200-2.000 operazioni shadow | $0.10 - $1.00 |
| **AWS IoT Jobs** | ~10-100 esecuzioni job | $0.01 - $0.10 |
| **AWS IoT Commands** | ~10-50 esecuzioni comandi | $0.01 - $0.05 |
| **Amazon S3** | Storage + richieste per firmware | $0.05 - $0.25 |
| **AWS IoT Fleet Indexing** | Query e indicizzazione dispositivi | $0.02 - $0.20 |
| **AWS IoT Device Management Software Package Catalog** | Operazioni sui pacchetti | $0.01 - $0.05 |
| **AWS IoT Device Management Bulk Registration** | Provisioning dispositivi in blocco | $0.05 - $0.50 |
| **AWS Identity and Access Management (IAM)** | Gestione ruoli/policy | $0.00 |
| **Totale Stimato** | **Sessione demo completa** | **$0.33 - $2.95** |

**Fattori di Costo:**
- Numero di dispositivi (100-10.000 configurabili)
- Frequenza di esecuzione dei job
- Operazioni di aggiornamento shadow
- Durata dello storage Amazon S3

**Gestione dei Costi:**
- ✅ Lo script di pulizia rimuove tutte le risorse
- ✅ Risorse demo di breve durata
- ✅ Scala configurabile (inizia in piccolo)
- ⚠️ **Ricordati di eseguire lo script di pulizia quando hai finito**

**📊 Monitora i costi:** [Dashboard di Fatturazione AWS](https://console.aws.amazon.com/billing/)

## 🚀 Avvio Rapido

```bash
# 1. Clona e configura
git clone https://github.com/aws-samples/sample-aws-iot-device-management-learning-path-basics.git
cd sample-aws-iot-device-management-learning-path-basics
python3 -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configura AWS
aws configure

# 3. Flusso di lavoro completo (ti consigliamo questa sequenza)
python scripts/provision_script.py        # Crea l'infrastruttura con tagging
python scripts/manage_dynamic_groups.py   # Crea gruppi di dispositivi
python scripts/manage_packages.py         # Gestisci i pacchetti firmware
python scripts/create_job.py              # Distribuisci aggiornamenti firmware
python scripts/simulate_job_execution.py  # Simula aggiornamenti dispositivi
python scripts/explore_jobs.py            # Monitora il progresso dei job
python scripts/manage_commands.py         # Invia comandi in tempo reale ai dispositivi
python scripts/manage_bulk_provisioning.py # Registrazione dispositivi in blocco (scala produttiva)
python scripts/cleanup_script.py          # Pulizia sicura con identificazione risorse
```

## 📚 Script Disponibili

| Script | Scopo | Funzionalità Principali |
|--------|---------|-------------|
| **provision_script.py** | Configurazione completa dell'infrastruttura | Crea dispositivi, gruppi, pacchetti, storage Amazon S3 |
| **manage_dynamic_groups.py** | Gestisci gruppi di dispositivi dinamici | Crea, elenca, elimina con validazione Fleet Indexing |
| **manage_packages.py** | Gestione completa dei pacchetti | Crea pacchetti/versioni, integrazione Amazon S3, tracciamento dispositivi con stato di ripristino individuale |
| **create_job.py** | Crea job di aggiornamento OTA | Targeting multi-gruppo, URL pre-firmati |
| **simulate_job_execution.py** | Simula aggiornamenti dispositivi | Download reali da Amazon S3, preparazione piano visibile, tracciamento progresso per dispositivo |
| **explore_jobs.py** | Monitora e gestisci i job | Esplorazione interattiva job, cancellazione, eliminazione e analisi |
| **manage_commands.py** | Invia comandi in tempo reale ai dispositivi | Gestione template, esecuzione comandi, monitoraggio stato, tracciamento cronologia |
| **manage_bulk_provisioning.py** | Registrazione dispositivi in blocco | Provisioning dispositivi su scala produttiva, generazione certificati, monitoraggio task |
| **cleanup_script.py** | Rimuovi risorse AWS | Pulizia selettiva, gestione costi |

## ⚙️ Configurazione

**Variabili d'Ambiente** (opzionali):
```bash
export AWS_DEFAULT_REGION=us-east-1
export AWS_IOT_LANG=it                    # Imposta la lingua predefinita (en, es, fr, ecc.)
```

**Funzionalità degli Script**:
- **AWS SDK Nativo**: Usa boto3 per prestazioni e affidabilità migliori
- **Supporto Multi-lingua**: Selezione interattiva della lingua con fallback all'inglese
- **Modalità Debug**: Mostra tutte le chiamate e risposte API AWS
- **Elaborazione Parallela**: Operazioni concorrenti quando non in modalità debug
- **Limitazione della Frequenza**: Conformità automatica al throttling API AWS
- **Tracciamento del Progresso**: Stato delle operazioni in tempo reale
- **Tagging delle Risorse**: Tag workshop automatici per pulizia sicura
- **Naming Configurabile**: Pattern di denominazione dispositivi personalizzabili

### Tagging delle Risorse

Tutti gli script del workshop taggano automaticamente le risorse create con `workshop=learning-aws-iot-dm-basics` per un'identificazione sicura durante la pulizia. Questo assicura che vengano eliminate solo le risorse create dal workshop.

**Risorse Taggate**:
- IoT Thing Types
- IoT Thing Groups (statici e dinamici)
- IoT Software Packages
- AWS IoT Jobs
- Bucket Amazon S3
- Ruoli AWS Identity and Access Management (IAM)

**Risorse Non Taggate** (identificate tramite pattern di denominazione):
- IoT Things (usano convenzioni di denominazione)
- Certificati (identificati per associazione)
- Thing Shadows (identificate per associazione)

### Configurazione Denominazione Dispositivi

Personalizza i pattern di denominazione dei dispositivi con il parametro `--things-prefix`:

```bash
# Denominazione predefinita: Vehicle-VIN-001, Vehicle-VIN-002, ecc.
python scripts/provision_script.py

# Prefisso personalizzato: Fleet-Device-001, Fleet-Device-002, ecc.
python scripts/provision_script.py --things-prefix "Fleet-Device-"

# Prefisso personalizzato per la pulizia (deve corrispondere al prefisso di provisioning)
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"
```

**Requisiti del Prefisso**:
- Usa caratteri alfanumerici, trattini, underscore e due punti
- Mantienilo sotto i 20 caratteri
- I numeri sequenziali vengono automaticamente riempiti con zeri (001-999)

## 🌍 Supporto Internazionalizzazione

Tutti gli script supportano più lingue con rilevamento automatico della lingua e selezione interattiva.

**Selezione della Lingua**:
- **Interattiva**: Gli script richiedono la selezione della lingua alla prima esecuzione
- **Variabile d'Ambiente**: Imposta `AWS_IOT_LANG=it` per saltare la selezione della lingua
- **Fallback**: Ritorna automaticamente all'inglese per traduzioni mancanti

**Lingue Supportate**:
- **English (en)**: Traduzioni complete ✅
- **Spanish (es)**: Pronto per le traduzioni
- **Japanese (ja)**: Pronto per le traduzioni  
- **Chinese (zh-CN)**: Pronto per le traduzioni
- **Portuguese (pt-BR)**: Pronto per le traduzioni
- **Korean (ko)**: Pronto per le traduzioni

**Esempi di Utilizzo**:
```bash
# Imposta la lingua tramite variabile d'ambiente (consigliato per l'automazione)
export AWS_IOT_LANG=it
python scripts/provision_script.py

# Codici lingua alternativi supportati
export AWS_IOT_LANG=spanish    # o "es", "español"
export AWS_IOT_LANG=japanese   # o "ja", "日本語", "jp"
export AWS_IOT_LANG=chinese    # o "zh-cn", "中文", "zh"
export AWS_IOT_LANG=portuguese # o "pt", "pt-br", "português"
export AWS_IOT_LANG=korean     # o "ko", "한국어", "kr"

# Selezione interattiva della lingua (comportamento predefinito)
python scripts/manage_packages.py
# Output: 🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择 / Seleção de Idioma / 언어 선택
#         1. English
#         2. Español (Spanish)
#         3. 日本語 (Japanese)
#         4. 中文 (Chinese)
#         5. Português (Portuguese)
#         6. 한국어 (Korean)
#         Select language (1-6): 

# Tutto il testo rivolto all'utente apparirà nella lingua selezionata
```

**Categorie di Messaggi**:
- **Elementi UI**: Titoli, intestazioni, separatori
- **Prompt Utente**: Richieste di input, conferme
- **Messaggi di Stato**: Aggiornamenti di progresso, notifiche di successo/fallimento
- **Messaggi di Errore**: Descrizioni dettagliate degli errori e risoluzione problemi
- **Output Debug**: Informazioni sulle chiamate API e risposte
- **Contenuti Didattici**: Momenti educativi e spiegazioni

## 📖 Esempi di Utilizzo

**Flusso di Lavoro Completo** (ti consigliamo questa sequenza):
```bash
python scripts/provision_script.py        # 1. Crea l'infrastruttura
python scripts/manage_dynamic_groups.py   # 2. Crea gruppi di dispositivi
python scripts/manage_packages.py         # 3. Gestisci i pacchetti firmware
python scripts/create_job.py              # 4. Distribuisci aggiornamenti firmware
python scripts/simulate_job_execution.py  # 5. Simula aggiornamenti dispositivi
python scripts/explore_jobs.py            # 6. Monitora il progresso dei job
python scripts/manage_commands.py         # 7. Invia comandi in tempo reale ai dispositivi
python scripts/cleanup_script.py          # 8. Pulisci le risorse
```

**Operazioni Individuali**:
```bash
python scripts/manage_packages.py         # Gestione pacchetti e versioni
python scripts/manage_dynamic_groups.py   # Operazioni sui gruppi dinamici
```

## 🛠️ Risoluzione dei Problemi

**Problemi Comuni**:
- **Credenziali**: Puoi configurare le credenziali AWS tramite `aws configure`, variabili d'ambiente o ruoli IAM
- **Permessi**: Assicurati che il tuo utente IAM abbia i permessi per AWS IoT, Amazon S3 e IAM
- **Limiti di Frequenza**: Non preoccuparti - gli script gestiscono questo automaticamente con throttling intelligente
- **Rete**: Assicurati di avere connettività alle API AWS

**Modalità Debug**: Puoi abilitarla in qualsiasi script per una risoluzione dettagliata dei problemi
```bash
🔧 Enable debug mode (show all API calls and responses)? [y/N]: y
```

> 📖 **Risoluzione Dettagliata dei Problemi**: Vedi [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) per soluzioni complete.

## 🧹 Importante: Pulizia delle Risorse

**Ricordati di eseguire la pulizia quando hai finito per evitare addebiti continui:**
```bash
python scripts/cleanup_script.py
# Scegli l'opzione 1: TUTTE le risorse
# Digita: DELETE
```

### Funzionalità di Pulizia Sicura

Lo script di pulizia usa più metodi di identificazione per assicurare che vengano eliminate solo le risorse del workshop:

1. **Identificazione Basata su Tag** (Primaria): Controlla il tag `workshop=learning-aws-iot-dm-basics`
2. **Corrispondenza Pattern di Denominazione** (Secondaria): Corrisponde alle convenzioni di denominazione note del workshop
3. **Basata su Associazione** (Terziaria): Identifica le risorse collegate alle risorse del workshop

**Opzioni di Pulizia**:
```bash
# Pulizia standard (interattiva)
python scripts/cleanup_script.py

# Modalità dry-run (anteprima senza eliminare)
python scripts/cleanup_script.py --dry-run

# Prefisso dispositivo personalizzato (deve corrispondere al prefisso di provisioning)
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"

# Dry-run con prefisso personalizzato
python scripts/cleanup_script.py --dry-run --things-prefix "Fleet-Device-"
```

**Cosa rimuove la pulizia:**
- Tutti i dispositivi e gruppi AWS IoT (con tag workshop o pattern di denominazione corrispondenti)
- Bucket Amazon S3 e file firmware (taggati)
- Pacchetti software AWS IoT (taggati)
- Template di comandi AWS IoT (taggati)
- Ruoli e policy IAM (taggati)
- Configurazione Fleet Indexing
- Certificati e shadow associati

**Funzionalità di Sicurezza**:
- Le risorse non del workshop vengono automaticamente saltate
- Vedrai un riepilogo dettagliato delle risorse eliminate e saltate
- La modalità debug mostra il metodo di identificazione per ogni risorsa
- La modalità dry-run ti permette di vedere un'anteprima prima dell'eliminazione effettiva

## 📁 Struttura del Progetto

```
sample-aws-iot-device-management-learning-path-basics/
├── scripts/                          # Script eseguibili rivolti all'utente
│   ├── provision_script.py          # Provisioning risorse IoT
│   ├── cleanup_script.py            # Pulizia risorse workshop
│   ├── manage_packages.py           # Gestione pacchetti
│   ├── manage_dynamic_groups.py     # Operazioni gruppi dinamici
│   ├── create_job.py                # Creazione job OTA
│   ├── simulate_job_execution.py    # Simulazione aggiornamenti dispositivi
│   ├── explore_jobs.py              # Monitoraggio progresso job
│   └── manage_commands.py           # Invio comandi in tempo reale
├── iot_helpers/                     # Pacchetto helper interno
│   ├── cleanup/                     # Moduli operazioni di pulizia
│   │   ├── reporter.py             # Reporting pulizia
│   │   ├── deletion_engine.py      # Eliminazione risorse
│   │   └── resource_identifier.py  # Identificazione risorse
│   └── utils/                       # Moduli utility
│       ├── naming_conventions.py   # Pattern di denominazione
│       ├── resource_tagger.py      # Tagging risorse
│       └── dependency_handler.py   # Gestione dipendenze
├── i18n/                            # Internazionalizzazione
│   ├── common.json                 # Messaggi condivisi
│   ├── loader.py                   # Caricamento messaggi
│   ├── language_selector.py        # Selezione lingua
│   └── {language_code}/            # Messaggi specifici per lingua
├── docs/                            # Documentazione
│   └── TROUBLESHOOTING.md          # Guida risoluzione problemi
├── tests/                           # File di test
└── requirements.txt                 # Dipendenze Python
```

## 🔧 Guida per Sviluppatori: Aggiungere Nuove Lingue

**Struttura dei File di Messaggi**:
```
i18n/
├── common.json                    # Messaggi condivisi tra tutti gli script
├── loader.py                      # Utility di caricamento messaggi
├── language_selector.py           # Interfaccia di selezione lingua
└── {language_code}/               # Directory specifica per lingua
    ├── provision_script.json     # Messaggi specifici dello script
    ├── manage_dynamic_groups.json
    ├── manage_packages.json
    ├── create_job.json
    ├── simulate_job_execution.json
    ├── explore_jobs.json
    └── cleanup_script.json
```

**Aggiungere una Nuova Lingua**:

1. **Crea la Directory della Lingua**:
   ```bash
   mkdir i18n/{language_code}  # es. i18n/it per l'italiano
   ```

2. **Copia i Template Inglesi**:
   ```bash
   cp i18n/en/*.json i18n/{language_code}/
   ```

3. **Traduci i File di Messaggi**:
   Ogni file JSON contiene messaggi categorizzati:
   ```json
   {
     "title": "📦 AWS IoT Software Package Manager (Boto3)",
     "separator": "============================================",
     "prompts": {
       "debug_mode": "🔧 Abilitare modalità debug? [y/N]: ",
       "operation_choice": "Inserisci scelta [1-11]: ",
       "continue_operation": "Continuare? [Y/n]: "
     },
     "status": {
       "debug_enabled": "✅ Modalità debug abilitata",
       "package_created": "✅ Pacchetto creato con successo",
       "clients_initialized": "🔍 DEBUG: Configurazione client:"
     },
     "errors": {
       "invalid_choice": "❌ Scelta non valida. Inserisci 1-11",
       "package_not_found": "❌ Pacchetto '{}' non trovato",
       "api_error": "❌ Errore in {} {}: {}"
     },
     "debug": {
       "api_call": "📤 Chiamata API: {}",
       "api_response": "📤 Risposta API:",
       "debug_operation": "🔍 DEBUG: {}: {}"
     },
     "ui": {
       "operation_menu": "🎯 Seleziona Operazione:",
       "create_package": "1. Crea Pacchetto Software",
       "goodbye": "👋 Grazie per aver usato Package Manager!"
     },
     "learning": {
       "package_management_title": "Gestione Pacchetti Software",
       "package_management_description": "Contenuto educativo..."
     }
   }
   ```

4. **Aggiorna il Selettore di Lingua** (se aggiungi una nuova lingua):
   Aggiungi la tua lingua a `i18n/language_selector.py`:
   ```python
   LANGUAGE_SELECTION = {
       "options": [
           "1. English",
           "2. Español (Spanish)",
           "3. Nome Tua Lingua",  # Aggiungi nuova opzione
           # ... lingue esistenti
       ],
   }
   
   LANGUAGE_CODES = {
       "1": "en", 
       "2": "es", 
       "3": "tuo_codice",  # Aggiungi nuovo codice lingua
       # ... mappature esistenti
   }
   ```

5. **Testa la Traduzione**:
   ```bash
   export AWS_IOT_LANG={language_code}
   python scripts/provision_script.py
   ```

**Linee Guida per la Traduzione**:
- **Preserva la Formattazione**: Mantieni emoji, colori e caratteri speciali così come sono
- **Mantieni i Segnaposto**: Mantieni i segnaposto `{}` per contenuti dinamici
- **Termini Tecnici**: Mantieni i nomi dei servizi AWS in inglese
- **Adattamento Culturale**: Sentiti libero di adattare esempi e riferimenti in modo appropriato
- **Coerenza**: Usa terminologia coerente in tutti i file

**Pattern delle Chiavi dei Messaggi**:
- `title`: Titolo principale dello script
- `separator`: Separatori visivi e divisori  
- `prompts.*`: Richieste di input utente e conferme
- `status.*`: Aggiornamenti di progresso e risultati operazioni
- `errors.*`: Messaggi di errore e avvisi
- `debug.*`: Output debug e informazioni API
- `ui.*`: Elementi interfaccia utente (menu, etichette, pulsanti)
- `results.*`: Risultati operazioni e visualizzazione dati
- `learning.*`: Contenuti educativi e spiegazioni
- `warnings.*`: Messaggi di avviso e avvisi importanti
- `explanations.*`: Contesto aggiuntivo e testi di aiuto

**Testare la Tua Traduzione**:
```bash
# Testa uno script specifico con la tua lingua
export AWS_IOT_LANG=tuo_codice_lingua
python scripts/manage_packages.py

# Testa il comportamento di fallback (usa una lingua non esistente)
export AWS_IOT_LANG=xx
python scripts/provision_script.py  # Dovrebbe tornare all'inglese
```

## 📚 Documentazione

- **[Risoluzione dei Problemi](docs/TROUBLESHOOTING.md)** - Problemi comuni e soluzioni

## 📄 Licenza

Licenza MIT No Attribution - vedi il file [LICENSE](LICENSE) per i dettagli.

## 🏷️ Tag

`aws` `aws-iot` `device-management` `ota-updates` `fleet-management` `python` `demo` `iot` 
