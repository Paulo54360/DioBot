# DioBot - Bot Discord de Modération

Un bot Discord conçu pour aider à la modération des serveurs Discord, avec des fonctionnalités de gestion des bannissements et de suivi des actions de modération.

## Fonctionnalités

- **Système de bannissement avec limites configurables par modérateur**
  - `!ban <membre> [raison]` - Bannir un membre du serveur
  - `!baninfo [membre]` - Afficher l'historique des bannissements
  
- **Gestion des modérateurs**
  - `!modlimit <membre> <limite> [limite_initiale] [jours_reset]` - Définir la limite de bannissements pour un modérateur
  - `!modstatus [membre]` - Afficher le statut d'un modérateur ou de tous les modérateurs
  
- **Suivi des actions de modération**
  - Enregistrement automatique de chaque bannissement
  - Historique consultable des actions de modération
  
- **Réinitialisation automatique des limites de bannissement**
  - Réinitialisation périodique configurable des limites de bannissement
  - Paramétrage flexible de la période de réinitialisation

- **Interface de commandes intuitive**
  - Commandes simples avec préfixe personnalisable
  - Messages d'erreur clairs et informatifs

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
   - Créez un fichier `.env` à la racine du projet avec le contenu suivant :
     ```
     DISCORD_TOKEN=votre_token_discord_ici
     BAN_ROLE_ID=id_du_role_moderateur
     ```
   - Remplacez les valeurs par vos propres informations

4. Lancez le bot :
   ```
   python bot.py
   ```

## Commandes

- `!ban <membre> [raison]` - Bannir un membre
- `!modlimit <membre> <limite> [limite_initiale] [jours_reset]` - Définir la limite de bannissements pour un modérateur
- `!modstatus [membre]` - Afficher le statut d'un modérateur ou de tous les modérateurs

## Tests

Le projet inclut une suite complète de tests unitaires pour garantir le bon fonctionnement du bot.

Pour exécuter les tests unitaires :
```bash
python run_tests.py
```

Les tests vérifient :
- Le fonctionnement des commandes de modération
- La gestion de la base de données
- Les utilitaires et fonctions auxiliaires
- La réinitialisation des limites de bannissement

Pour générer un rapport de test détaillé :
```bash
python run_tests.py --report
```

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails. 