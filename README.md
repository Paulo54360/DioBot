# DioBot - Bot Discord de Modération

Un bot Discord conçu pour aider à la modération des serveurs Discord, avec des fonctionnalités de gestion des bannissements et de suivi des actions de modération.

## Fonctionnalités

- Système de bannissement avec limites configurables par modérateur
- Suivi des actions de modération
- Réinitialisation automatique des limites de bannissement
- Interface de commandes intuitive

## Installation

1. Clonez ce dépôt :
   ```
   git clone https://github.com/votre-username/diobot.git
   cd diobot
   ```

2. Installez les dépendances :
   ```
   pip install -r requirements.txt
   ```

3. Configurez le bot :
   - Créez un fichier `config.json` basé sur `config.example.json`
   - Ajoutez votre token Discord et autres paramètres

4. Lancez le bot :
   ```
   python bot.py
   ```

## Commandes

- `!ban <membre> [raison]` - Bannir un membre
- `!modlimit <membre> <limite> [limite_initiale] [jours_reset]` - Définir la limite de bannissements pour un modérateur
- `!modstatus [membre]` - Afficher le statut d'un modérateur ou de tous les modérateurs

## Tests

Pour exécuter les tests unitaires : 