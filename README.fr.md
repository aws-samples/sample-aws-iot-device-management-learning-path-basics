# AWS IoT Device Management - Parcours d'Apprentissage - Bases

## 🌍 Langues Disponibles | Available Languages | Idiomas Disponibles | 利用可能な言語 | 사용 가능한 언어 | Idiomas Disponíveis | 可用语言

| Langue | README |
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

Une démonstration complète des capacités d'AWS IoT Device Management, incluant le provisionnement d'appareils, les mises à jour OTA (over-the-air), la gestion des tâches et les opérations de flotte. Ce projet utilise des scripts Python modernes avec l'intégration native du SDK AWS (boto3) pour t'aider à apprendre ces concepts de manière pratique.

## 👥 Public Cible

**Public Principal :** Développeurs IoT, architectes de solutions et ingénieurs DevOps travaillant avec des flottes d'appareils AWS IoT

**Prérequis :** Connaissances intermédiaires d'AWS, fondamentaux d'AWS IoT Core, fondamentaux de Python et utilisation de la ligne de commande

**Niveau d'Apprentissage :** Niveau associé avec une approche pratique de la gestion d'appareils à grande échelle

## 🎯 Objectifs d'Apprentissage

- **Gestion du Cycle de Vie des Appareils** : Provisionner des appareils IoT avec les types et attributs appropriés
- **Organisation de Flotte** : Créer des groupes d'appareils statiques et dynamiques pour la gestion
- **Mises à Jour OTA** : Implémenter des mises à jour de firmware en utilisant AWS IoT Jobs avec l'intégration Amazon S3
- **Gestion de Packages** : Gérer plusieurs versions de firmware avec des mises à jour automatiques des shadows
- **Exécution de Tâches** : Simuler un comportement réaliste des appareils pendant les mises à jour de firmware
- **Contrôle de Version** : Revenir à des versions précédentes de firmware pour les appareils
- **Commandes à Distance** : Envoyer des commandes en temps réel aux appareils en utilisant AWS IoT Commands
- **Enregistrement en Masse** : Enregistrer des centaines ou des milliers d'appareils efficacement en utilisant un provisionnement à l'échelle de la fabrication
- **Nettoyage des Ressources** : Gérer correctement les ressources AWS pour éviter des coûts inutiles



## 📋 Prérequis

- **Compte AWS** avec les permissions AWS IoT, Amazon S3 et AWS Identity and Access Management (IAM)
- **Identifiants AWS** configurés (tu peux utiliser `aws configure`, des variables d'environnement ou des rôles IAM)
- **Python 3.10+** avec pip et les bibliothèques Python boto3, colorama et requests (consulte le fichier requirements.txt)
- **Git** pour cloner le dépôt

## 💰 Analyse des Coûts

**Ce projet crée de vraies ressources AWS qui entraîneront des frais. Voici à quoi t'attendre :**

| Service | Utilisation | Coût Estimé (USD) |
|---------|-------|---------------------|
| **AWS IoT Core** | ~1 000 messages, 100-10 000 appareils | 0,08 $ - 0,80 $ |
| **AWS IoT Device Shadow** | ~200-2 000 opérations shadow | 0,10 $ - 1,00 $ |
| **AWS IoT Jobs** | ~10-100 exécutions de tâches | 0,01 $ - 0,10 $ |
| **AWS IoT Commands** | ~10-50 exécutions de commandes | 0,01 $ - 0,05 $ |
| **Amazon S3** | Stockage + requêtes pour firmware | 0,05 $ - 0,25 $ |
| **AWS IoT Fleet Indexing** | Requêtes et indexation d'appareils | 0,02 $ - 0,20 $ |
| **AWS IoT Device Management Software Package Catalog** | Opérations de packages | 0,01 $ - 0,05 $ |
| **AWS IoT Device Management Bulk Registration** | Provisionnement en masse d'appareils | 0,05 $ - 0,50 $ |
| **AWS Identity and Access Management (IAM)** | Gestion des rôles/politiques | 0,00 $ |
| **Total Estimé** | **Session de démo complète** | **0,33 $ - 2,95 $** |

**Facteurs de Coût :**
- Nombre d'appareils (100-10 000 configurable)
- Fréquence d'exécution des tâches
- Opérations de mise à jour des shadows
- Durée de stockage Amazon S3

**Gestion des Coûts :**
- ✅ Le script de nettoyage supprime toutes les ressources
- ✅ Ressources de démo de courte durée
- ✅ Échelle configurable (commence petit)
- ⚠️ **N'oublie pas d'exécuter le script de nettoyage quand tu as terminé**

**📊 Surveille les coûts :** [Tableau de Bord de Facturation AWS](https://console.aws.amazon.com/billing/)

## 🚀 Démarrage Rapide

```bash
# 1. Cloner et configurer
git clone https://github.com/aws-samples/sample-aws-iot-device-management-learning-path-basics.git
cd sample-aws-iot-device-management-learning-path-basics
python3 -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
pip install -r requirements.txt

# 2. Configurer AWS
aws configure

# 3. Flux de travail complet (nous recommandons cette séquence)
python scripts/provision_script.py        # Créer l'infrastructure avec le marquage
python scripts/manage_dynamic_groups.py   # Créer des groupes d'appareils
python scripts/manage_packages.py         # Gérer les packages de firmware
python scripts/create_job.py              # Déployer les mises à jour de firmware
python scripts/simulate_job_execution.py  # Simuler les mises à jour d'appareils
python scripts/explore_jobs.py            # Surveiller la progression des tâches
python scripts/manage_commands.py         # Envoyer des commandes en temps réel aux appareils
python scripts/manage_bulk_provisioning.py # Enregistrement en masse d'appareils (échelle de fabrication)
python scripts/cleanup_script.py          # Nettoyage sécurisé avec identification des ressources
```

## 📚 Scripts Disponibles

| Script | Objectif | Fonctionnalités Clés |
|--------|---------|-------------|
| **provision_script.py** | Configuration complète de l'infrastructure | Crée des appareils, groupes, packages, stockage Amazon S3 |
| **manage_dynamic_groups.py** | Gérer les groupes d'appareils dynamiques | Créer, lister, supprimer avec validation Fleet Indexing |
| **manage_packages.py** | Gestion complète des packages | Créer packages/versions, intégration Amazon S3, suivi des appareils avec statut de retour individuel |
| **create_job.py** | Créer des tâches de mise à jour OTA | Ciblage multi-groupes, URLs présignées |
| **simulate_job_execution.py** | Simuler les mises à jour d'appareils | Téléchargements réels Amazon S3, préparation de plan visible, suivi de progression par appareil |
| **explore_jobs.py** | Surveiller et gérer les tâches | Exploration interactive des tâches, annulation, suppression et analyses |
| **manage_commands.py** | Envoyer des commandes en temps réel aux appareils | Gestion de modèles, exécution de commandes, surveillance de statut, suivi d'historique |
| **manage_bulk_provisioning.py** | Enregistrement en masse d'appareils | Provisionnement d'appareils à l'échelle de la fabrication, génération de certificats, surveillance des tâches |
| **cleanup_script.py** | Supprimer les ressources AWS | Nettoyage sélectif, gestion des coûts |

## ⚙️ Configuration

**Variables d'Environnement** (optionnel) :
```bash
export AWS_DEFAULT_REGION=us-east-1
export AWS_IOT_LANG=fr                    # Définir la langue par défaut (en, es, fr, etc.)
```

**Fonctionnalités des Scripts** :
- **SDK AWS Natif** : Utilise boto3 pour de meilleures performances et fiabilité
- **Support Multi-langue** : Sélection interactive de langue avec repli sur l'anglais
- **Mode Debug** : Affiche tous les appels et réponses de l'API AWS
- **Traitement Parallèle** : Opérations concurrentes quand pas en mode debug
- **Limitation de Débit** : Conformité automatique à la limitation de l'API AWS
- **Suivi de Progression** : Statut des opérations en temps réel
- **Marquage des Ressources** : Marquage automatique de l'atelier pour un nettoyage sécurisé
- **Nommage Configurable** : Modèles de nommage d'appareils personnalisables

### Marquage des Ressources

Tous les scripts de l'atelier marquent automatiquement les ressources créées avec `workshop=learning-aws-iot-dm-basics` pour une identification sécurisée pendant le nettoyage. Cela garantit que seules les ressources créées par l'atelier sont supprimées.

**Ressources Marquées** :
- Types de Things IoT
- Groupes de Things IoT (statiques et dynamiques)
- Packages Logiciels IoT
- AWS IoT Jobs
- Buckets Amazon S3
- Rôles AWS Identity and Access Management (IAM)

**Ressources Non Marquées** (identifiées par modèles de nommage) :
- Things IoT (utilisent des conventions de nommage)
- Certificats (identifiés par association)
- Thing Shadows (identifiés par association)

### Configuration du Nommage des Appareils

Personnalise les modèles de nommage des appareils avec le paramètre `--things-prefix` :

```bash
# Nommage par défaut : Vehicle-VIN-001, Vehicle-VIN-002, etc.
python scripts/provision_script.py

# Préfixe personnalisé : Fleet-Device-001, Fleet-Device-002, etc.
python scripts/provision_script.py --things-prefix "Fleet-Device-"

# Préfixe personnalisé pour le nettoyage (doit correspondre au préfixe de provisionnement)
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"
```

**Exigences du Préfixe** :
- Utilise des caractères alphanumériques, tirets, underscores et deux-points
- Garde-le sous 20 caractères
- Les numéros séquentiels sont automatiquement complétés avec des zéros (001-999)

## 🌍 Support d'Internationalisation

Tous les scripts supportent plusieurs langues avec détection automatique de langue et sélection interactive.

**Sélection de Langue** :
- **Interactive** : Les scripts demandent la sélection de langue au premier lancement
- **Variable d'Environnement** : Définis `AWS_IOT_LANG=fr` pour sauter la sélection de langue
- **Repli** : Repli automatique sur l'anglais pour les traductions manquantes

**Langues Supportées** :
- **English (en)** : Traductions complètes ✅
- **Spanish (es)** : Prêt pour les traductions
- **Japanese (ja)** : Prêt pour les traductions  
- **Chinese (zh-CN)** : Prêt pour les traductions
- **Portuguese (pt-BR)** : Prêt pour les traductions
- **Korean (ko)** : Prêt pour les traductions
- **German (de)** : Prêt pour les traductions
- **Italian (it)** : Prêt pour les traductions
- **French (fr)** : Prêt pour les traductions

**Exemples d'Utilisation** :
```bash
# Définir la langue via variable d'environnement (recommandé pour l'automatisation)
export AWS_IOT_LANG=fr
python scripts/provision_script.py

# Codes de langue alternatifs supportés
export AWS_IOT_LANG=french     # ou "fr", "français", "francais"
export AWS_IOT_LANG=spanish    # ou "es", "español"
export AWS_IOT_LANG=japanese   # ou "ja", "日本語", "jp"
export AWS_IOT_LANG=chinese    # ou "zh-cn", "中文", "zh"
export AWS_IOT_LANG=portuguese # ou "pt", "pt-br", "português"
export AWS_IOT_LANG=korean     # ou "ko", "한국어", "kr"
export AWS_IOT_LANG=german     # ou "de", "deutsch"
export AWS_IOT_LANG=italian    # ou "it", "italiano"

# Sélection interactive de langue (comportement par défaut)
python scripts/manage_packages.py
# Sortie : 🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择 / Seleção de Idioma / 언어 선택 / Sprachauswahl / Selezione della Lingua / Sélection de la Langue
#         1. English
#         2. Español (Spanish)
#         3. 日本語 (Japanese)
#         4. 中文 (Chinese)
#         5. Português (Portuguese)
#         6. 한국어 (Korean)
#         7. Deutsch (German)
#         8. Italiano (Italian)
#         9. Français (French)
#         Select language (1-9): 

# Tout le texte destiné à l'utilisateur apparaîtra dans la langue sélectionnée
```

**Catégories de Messages** :
- **Éléments d'Interface** : Titres, en-têtes, séparateurs
- **Invites Utilisateur** : Demandes de saisie, confirmations
- **Messages de Statut** : Mises à jour de progression, notifications de succès/échec
- **Messages d'Erreur** : Descriptions d'erreur détaillées et dépannage
- **Sortie Debug** : Informations sur les appels API et réponses
- **Contenu d'Apprentissage** : Moments éducatifs et explications

## 📖 Exemples d'Utilisation

**Flux de Travail Complet** (nous recommandons cette séquence) :
```bash
python scripts/provision_script.py        # 1. Créer l'infrastructure
python scripts/manage_dynamic_groups.py   # 2. Créer des groupes d'appareils
python scripts/manage_packages.py         # 3. Gérer les packages de firmware
python scripts/create_job.py              # 4. Déployer les mises à jour de firmware
python scripts/simulate_job_execution.py  # 5. Simuler les mises à jour d'appareils
python scripts/explore_jobs.py            # 6. Surveiller la progression des tâches
python scripts/manage_commands.py         # 7. Envoyer des commandes en temps réel aux appareils
python scripts/cleanup_script.py          # 8. Nettoyer les ressources
```

**Opérations Individuelles** :
```bash
python scripts/manage_packages.py         # Gestion de packages et versions
python scripts/manage_dynamic_groups.py   # Opérations de groupes dynamiques
```

## 🛠️ Dépannage

**Problèmes Courants** :
- **Identifiants** : Tu peux configurer les identifiants AWS via `aws configure`, des variables d'environnement ou des rôles IAM
- **Permissions** : Assure-toi que ton utilisateur IAM a les permissions AWS IoT, Amazon S3 et IAM
- **Limites de Débit** : Ne t'inquiète pas - les scripts gèrent cela automatiquement avec une limitation intelligente
- **Réseau** : Assure-toi d'avoir une connectivité aux APIs AWS

**Mode Debug** : Tu peux activer ceci dans n'importe quel script pour un dépannage détaillé
```bash
🔧 Activer le mode debug (afficher tous les appels et réponses API) ? [y/N] : y
```

> 📖 **Dépannage Détaillé** : Consulte [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) pour des solutions complètes.

## 🧹 Important : Nettoyage des Ressources

**N'oublie pas d'exécuter le nettoyage quand tu as terminé pour éviter des frais continus :**
```bash
python scripts/cleanup_script.py
# Choisis l'option 1 : TOUTES les ressources
# Tape : DELETE
```

### Fonctionnalités de Nettoyage Sécurisé

Le script de nettoyage utilise plusieurs méthodes d'identification pour garantir que seules les ressources de l'atelier sont supprimées :

1. **Identification Basée sur les Marqueurs** (Principal) : Vérifie le marqueur `workshop=learning-aws-iot-dm-basics`
2. **Correspondance de Modèle de Nommage** (Secondaire) : Correspond aux conventions de nommage connues de l'atelier
3. **Basé sur l'Association** (Tertiaire) : Identifie les ressources attachées aux ressources de l'atelier

**Options de Nettoyage** :
```bash
# Nettoyage standard (interactif)
python scripts/cleanup_script.py

# Mode simulation (aperçu sans supprimer)
python scripts/cleanup_script.py --dry-run

# Préfixe d'appareil personnalisé (doit correspondre au préfixe de provisionnement)
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"

# Simulation avec préfixe personnalisé
python scripts/cleanup_script.py --dry-run --things-prefix "Fleet-Device-"
```

**Ce que le nettoyage supprime** :
- Tous les appareils et groupes AWS IoT (avec marqueurs d'atelier ou modèles de nommage correspondants)
- Buckets Amazon S3 et fichiers de firmware (marqués)
- Packages logiciels AWS IoT (marqués)
- Modèles de commandes AWS IoT (marqués)
- Rôles et politiques IAM (marqués)
- Configuration Fleet Indexing
- Certificats et shadows associés

**Fonctionnalités de Sécurité** :
- Les ressources hors atelier sont automatiquement ignorées
- Tu verras un résumé détaillé des ressources supprimées et ignorées
- Le mode debug affiche la méthode d'identification pour chaque ressource
- Le mode simulation te permet de prévisualiser avant la suppression réelle

## 📁 Structure du Projet

```
sample-aws-iot-device-management-learning-path-basics/
├── scripts/                          # Scripts exécutables destinés à l'utilisateur
│   ├── provision_script.py          # Provisionner les ressources IoT
│   ├── cleanup_script.py            # Nettoyer les ressources de l'atelier
│   ├── manage_packages.py           # Gestion de packages
│   ├── manage_dynamic_groups.py     # Opérations de groupes dynamiques
│   ├── create_job.py                # Créer des tâches OTA
│   ├── simulate_job_execution.py    # Simuler les mises à jour d'appareils
│   ├── explore_jobs.py              # Surveiller la progression des tâches
│   └── manage_commands.py           # Envoyer des commandes en temps réel
├── iot_helpers/                     # Package d'aide interne
│   ├── cleanup/                     # Modules d'opérations de nettoyage
│   │   ├── reporter.py             # Rapport de nettoyage
│   │   ├── deletion_engine.py      # Suppression de ressources
│   │   └── resource_identifier.py  # Identification de ressources
│   └── utils/                       # Modules utilitaires
│       ├── naming_conventions.py   # Modèles de nommage
│       ├── resource_tagger.py      # Marquage de ressources
│       └── dependency_handler.py   # Gestion des dépendances
├── i18n/                            # Internationalisation
│   ├── common.json                 # Messages partagés
│   ├── loader.py                   # Chargement de messages
│   ├── language_selector.py        # Sélection de langue
│   └── {language_code}/            # Messages spécifiques à la langue
├── docs/                            # Documentation
│   └── TROUBLESHOOTING.md          # Guide de dépannage
├── tests/                           # Fichiers de test
└── requirements.txt                 # Dépendances Python
```

## 🔧 Guide Développeur : Ajouter de Nouvelles Langues

**Structure des Fichiers de Messages** :
```
i18n/
├── common.json                    # Messages partagés entre tous les scripts
├── loader.py                      # Utilitaire de chargement de messages
├── language_selector.py           # Interface de sélection de langue
└── {language_code}/               # Répertoire spécifique à la langue
    ├── provision_script.json     # Messages spécifiques au script
    ├── manage_dynamic_groups.json
    ├── manage_packages.json
    ├── create_job.json
    ├── simulate_job_execution.json
    ├── explore_jobs.json
    └── cleanup_script.json
```

**Ajouter une Nouvelle Langue** :

1. **Créer le Répertoire de Langue** :
   ```bash
   mkdir i18n/{language_code}  # ex., i18n/fr pour le français
   ```

2. **Copier les Modèles Anglais** :
   ```bash
   cp i18n/en/*.json i18n/{language_code}/
   ```

3. **Traduire les Fichiers de Messages** :
   Chaque fichier JSON contient des messages catégorisés :
   ```json
   {
     "title": "📦 AWS IoT Software Package Manager (Boto3)",
     "separator": "============================================",
     "prompts": {
       "debug_mode": "🔧 Activer le mode debug ? [y/N] : ",
       "operation_choice": "Entrer le choix [1-11] : ",
       "continue_operation": "Continuer ? [Y/n] : "
     },
     "status": {
       "debug_enabled": "✅ Mode debug activé",
       "package_created": "✅ Package créé avec succès",
       "clients_initialized": "🔍 DEBUG : Configuration du client :"
     },
     "errors": {
       "invalid_choice": "❌ Choix invalide. Veuillez entrer 1-11",
       "package_not_found": "❌ Package '{}' non trouvé",
       "api_error": "❌ Erreur dans {} {} : {}"
     },
     "debug": {
       "api_call": "📤 Appel API : {}",
       "api_response": "📤 Réponse API :",
       "debug_operation": "🔍 DEBUG : {} : {}"
     },
     "ui": {
       "operation_menu": "🎯 Sélectionner l'Opération :",
       "create_package": "1. Créer un Package Logiciel",
       "goodbye": "👋 Merci d'avoir utilisé le Gestionnaire de Packages !"
     },
     "learning": {
       "package_management_title": "Gestion de Packages Logiciels",
       "package_management_description": "Contenu éducatif..."
     }
   }
   ```

4. **Mettre à Jour le Sélecteur de Langue** (si ajout d'une nouvelle langue) :
   Ajoute ta langue à `i18n/language_selector.py` :
   ```python
   LANGUAGE_SELECTION = {
       "options": [
           "1. English",
           "2. Español (Spanish)",
           "3. Nom de Ta Langue",  # Ajouter nouvelle option
           # ... langues existantes
       ],
   }
   
   LANGUAGE_CODES = {
       "1": "en", 
       "2": "es", 
       "3": "ton_code",  # Ajouter nouveau code de langue
       # ... mappages existants
   }
   ```

5. **Tester la Traduction** :
   ```bash
   export AWS_IOT_LANG={language_code}
   python scripts/provision_script.py
   ```

**Directives de Traduction** :
- **Préserver le Formatage** : Garde les emojis, couleurs et caractères spéciaux tels quels
- **Maintenir les Espaces Réservés** : Garde les espaces réservés `{}` pour le contenu dynamique
- **Termes Techniques** : Garde les noms de services AWS en anglais
- **Adaptation Culturelle** : N'hésite pas à adapter les exemples et références de manière appropriée
- **Cohérence** : Utilise une terminologie cohérente dans tous les fichiers

**Modèles de Clés de Messages** :
- `title` : Titre principal du script
- `separator` : Séparateurs visuels et diviseurs  
- `prompts.*` : Demandes de saisie utilisateur et confirmations
- `status.*` : Mises à jour de progression et résultats d'opération
- `errors.*` : Messages d'erreur et avertissements
- `debug.*` : Sortie debug et informations API
- `ui.*` : Éléments d'interface utilisateur (menus, étiquettes, boutons)
- `results.*` : Résultats d'opération et affichage de données
- `learning.*` : Contenu éducatif et explications
- `warnings.*` : Messages d'avertissement et avis importants
- `explanations.*` : Contexte supplémentaire et textes d'aide

**Tester Ta Traduction** :
```bash
# Tester un script spécifique avec ta langue
export AWS_IOT_LANG=ton_code_de_langue
python scripts/manage_packages.py

# Tester le comportement de repli (utiliser une langue inexistante)
export AWS_IOT_LANG=xx
python scripts/provision_script.py  # Devrait revenir à l'anglais
```

## 📚 Documentation

- **[Dépannage](docs/TROUBLESHOOTING.md)** - Problèmes courants et solutions

## 📄 Licence

Licence MIT No Attribution - consulte le fichier [LICENSE](LICENSE) pour les détails.

## 🏷️ Tags

`aws` `aws-iot` `device-management` `ota-updates` `fleet-management` `python` `demo` `iot` 
