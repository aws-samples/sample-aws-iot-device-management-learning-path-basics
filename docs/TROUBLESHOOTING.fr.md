# Guide de Dépannage

Ce guide t'aide à résoudre les problèmes de configuration de l'environnement. Si tu rencontres des problèmes spécifiques aux scripts, essaie d'activer le mode débogage lors de l'exécution - il te donnera des messages d'erreur utiles et des conseils tout au long du processus.

## Configuration de l'Environnement

### Configuration des Identifiants AWS

#### Problème : "Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**Voici comment le résoudre** :
```bash
# Configure les identifiants AWS
aws configure
# Entre : Access Key ID, Secret Access Key, Region, Output format

# Vérifie la configuration
aws sts get-caller-identity
```

**Tu peux aussi essayer ces méthodes alternatives** :
- Variables d'environnement : `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Fichier d'identifiants AWS : `~/.aws/credentials`
- Rôles IAM (si tu exécutes sur EC2 ou Lambda)

---

### Configuration de la Région

#### Problème : "Region not configured" ou "You must specify a region"

**Voici comment le résoudre** :
```bash
# Définis la région dans AWS CLI
aws configure set region us-east-1

# Ou utilise une variable d'environnement
export AWS_DEFAULT_REGION=us-east-1

# Vérifie la région
aws configure get region
```

**Fonctionne avec ces régions** : N'importe quelle région AWS où IoT Core est disponible

---

### Dépendances Python

#### Problème : "No module named 'colorama'" ou erreurs d'importation similaires
```
ModuleNotFoundError: No module named 'colorama'
```

**Voici comment le résoudre** :
```bash
# Installe toutes les dépendances
pip install -r requirements.txt

# Ou installe individuellement
pip install boto3>=1.40.27 colorama>=0.4.4 requests>=2.25.1
```

**Tu peux vérifier ton installation comme ça** :
```bash
python -c "import boto3, colorama, requests; print('All dependencies installed')"
```

---

### Permissions IAM

#### Problème : Erreurs "Access Denied" ou "User is not authorized"
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**Voici comment le résoudre** : Assure-toi que ton utilisateur ou rôle IAM AWS a les permissions nécessaires :

**Ce dont tu auras besoin - Actions IAM** :
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

**Petite note** : Pour les environnements de production, c'est une bonne idée de suivre le principe du moindre privilège et de restreindre les ressources selon les besoins.

---

## Obtenir de l'Aide

### Problèmes Spécifiques aux Scripts

Si tu rencontres des problèmes lors de l'exécution des scripts, voici quelques conseils utiles :

1. **Active le mode débogage** - Il te montrera les appels API détaillés et les réponses
   ```
   🔧 Enable debug mode? [y/N]: y
   ```

2. **Lis les messages d'erreur** - Les scripts fournissent des conseils contextuels utiles

3. **Consulte les pauses éducatives** - Elles expliquent les concepts et les exigences au fur et à mesure

4. **Vérifie les prérequis** - La plupart des scripts nécessitent l'exécution de `provision_script.py` en premier

### Voici un flux de travail typique

```bash
# 1. Configure ton environnement (une seule fois)
aws configure
export AWS_DEFAULT_REGION=us-east-1
pip install -r requirements.txt

# 2. Crée ton infrastructure (exécute ça en premier)
python scripts/provision_script.py

# 3. Exécute les autres scripts selon tes besoins
python scripts/manage_packages.py
python scripts/create_job.py
# etc.

# 4. Nettoie quand tu as terminé
python scripts/cleanup_script.py
```

### Ressources supplémentaires utiles

- **README.md** - Aperçu du projet et guide de démarrage rapide
- **Messages i18n des scripts** - Conseils utiles dans ta langue
- **Pauses éducatives** - Apprends au fur et à mesure pendant l'exécution des scripts
- **Documentation AWS IoT** - https://docs.aws.amazon.com/iot/
