# DioBot - Bot Discord de Modération

Un bot Discord conçu pour aider à la modération des serveurs Discord, avec des fonctionnalités de gestion des bannissements et de suivi des actions de modération.

## Fonctionnalités

- **Système de bannissement avec limites configurables par modérateur**
  - `/ban <membre> [raison]` - Bannir un membre du serveur
  
- **Gestion des modérateurs**
  - `/setban <membre> <nombre_bans_initial> <jours_reset>` - Définir le nombre de bans et le timer de réinitialisation pour un modérateur
  
- **Suivi des actions de modération**
  - `/banhistory [membre]` - Afficher l'historique des bans pour un utilisateur spécifique ou pour tous les utilisateurs
  
- **Affichage des limites de bans**
  - `/banlimits` - Affiche la liste des bans restants pour tous les modérateurs, ainsi que le temps restant avant la réinitialisation des bans.

## Permissions

Toutes les commandes de modération sont restreintes aux utilisateurs ayant le rôle admin. Pour configurer ce rôle :

1. Créez un rôle admin sur votre serveur Discord.
2. Ajoutez l'ID du rôle dans le fichier `.env` :
   ```
   ADMIN_ROLE_ID=id_du_role_admin
   ```
3. Attribuez ce rôle aux utilisateurs qui doivent avoir accès aux commandes de modération.

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
     ADMIN_ROLE_ID=id_du_role_admin
     ```
   - Remplacez les valeurs par vos propres informations.

4. Lancez le bot :
   ```
   python bot.py
   ```

## Cogs

Le bot utilise des cogs pour organiser les commandes et la logique. Chaque cog est un module qui regroupe des fonctionnalités spécifiques. Par exemple, le cog `ban_commands.py` contient toutes les commandes liées à la gestion des bans.

### Structure des Fichiers

- **`cogs/moderation/commands/ban_commands.py`** : Contient les commandes de modération liées aux bans, y compris `/ban`, `/setban`, `/banhistory`, et `/banlimits`.
- **`cogs/moderation/database/database.py`** : Gère les interactions avec la base de données, y compris la récupération et la mise à jour des données des modérateurs et des bans.
- **`bot.py`** : Point d'entrée du bot, où le bot est initialisé et les cogs sont chargés.

## Tests

Le projet inclut une suite complète de tests unitaires pour garantir le bon fonctionnement du bot.

Pour exécuter les tests unitaires :
```