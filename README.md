Voici une version corrigée et améliorée du fichier `.md` :

# DioBot - Bot Discord de Modération

Un bot Discord conçu pour aider à la modération des serveurs Discord, avec des fonctionnalités avancées de gestion des bannissements et de suivi des actions de modération.

---

## Fonctionnalités

### 🛡️ Système de bannissement intelligent
- **`/ban <membre> [raison]`**  
  Bannir un membre du serveur avec un système de quotas configurables

### 👮 Gestion des modérateurs
- **`/setban <membre> <nombre_bans_initial> <jours_reset>`**  
  Configurer les limites de bannissement par modérateur

### 📊 Suivi des actions
- **`/banhistory [membre]`**  
  Afficher l'historique complet des bannissements (spécifique ou global)

### ⏱️ Contrôle des limites
- **`/banlimits`**  
  Visualiser les quotas restants et le temps avant réinitialisation

---

## 🔒 Permissions

Toutes les commandes de modération nécessitent le rôle administrateur.

**Configuration :**
1. Créez un rôle admin sur votre serveur
2. Ajoutez l'ID dans `.env` :
   ```env
   ADMIN_ROLE_ID=votre_id_ici
   ```
3. Attribuez ce rôle aux modérateurs

---

## 🛠️ Installation

### Prérequis
- Python 3.8+
- Compte Discord Developer

### Étapes :
```bash
git clone https://github.com/Paulo54360/DioBot.git
cd DioBot
pip install -r requirements.txt
```

### Configuration
Créez/modifiez le fichier `.env` :
```env
DISCORD_TOKEN=votre_token
BAN_ROLE_ID=id_moderateur
ADMIN_ROLE_ID=id_admin
```

### Lancement
```bash
python bot.py
```

---

## 🧩 Architecture

### Structure des Cogs
```
DioBot/
├── cogs/
│   ├── listeners/messages/      # Événements messages
│   ├── moderation/commands/     # Commandes de modération
│   └── moderation/database/     # Gestion base de données
```

### Fichiers Principaux
- **`bot.py`** : Point d'entrée principal
- **`ban_commands.py`** : Commandes de bannissement
- **`database.py`** : Interactions avec la DB

---

## 🧪 Tests

Suite de tests complète couvrant :
- Commandes
- Base de données
- Événements
- Utilitaires

### Exécution
```bash
python run_tests.py
```

### Structure des Tests
```
tests/
├── conftest.py
├── test_commands.py
├── test_database.py
├── test_listeners.py
└── test_utils.py
```

### Rapports
Les résultats sont générés au format HTML dans :
```
test-reports/
```

---

> **Note** : Le bot nécessite les permissions `BAN_MEMBERS` et `VIEW_AUDIT_LOG` pour fonctionner correctement.
