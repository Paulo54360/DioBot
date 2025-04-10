import sqlite3
import os
import logging
from datetime import datetime

logger = logging.getLogger("moderation")

class ModerationDB:
    """Gère les interactions avec la base de données pour le module de modération."""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Créer la table des modérateurs
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS moderators (
                user_id INTEGER PRIMARY KEY,
                ban_limit INTEGER,
                initial_limit INTEGER,
                reset_date TEXT,
                username TEXT
            )
            ''')
            
            # Créer la table de l'historique des bans
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ban_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                moderator_id INTEGER,
                banned_user_id INTEGER,
                banned_user_name TEXT,
                reason TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info(f"Base de données initialisée avec succès: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
            return False
    
    def get_moderator_data(self, user_id):
        """Récupère les données d'un modérateur depuis la base de données."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM moderators WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "user_id": result[0],
                    "ban_limit": result[1],
                    "initial_limit": result[2],
                    "reset_date": result[3],
                    "username": result[4]
                }
            logger.warning(f"Aucun modérateur trouvé pour l'utilisateur ID: {user_id}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données du modérateur: {e}")
            return None
        
    def update_moderator_ban_limit(self, user_id, new_ban_limit):
        """Met à jour la limite de bans d'un modérateur dans la base de données."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE moderators SET ban_limit = ? WHERE user_id = ?",
                (new_ban_limit, user_id)
            )
            
            conn.commit()
            conn.close()
            logger.info(f"Limite de bans mise à jour pour l'utilisateur ID: {user_id} à {new_ban_limit}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la limite de bans: {e}")
            return False
    
    def get_all_moderators(self):
        """Récupère tous les modérateurs depuis la base de données."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM moderators")
            results = cursor.fetchall()
            conn.close()
            
            moderators = []
            for result in results:
                moderators.append({
                    "user_id": result[0],
                    "ban_limit": result[1],
                    "initial_limit": result[2],
                    "reset_date": result[3],
                    "username": result[4]
                })
            return moderators
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de tous les modérateurs: {e}")
            return []
    
    def set_moderator_data(self, user_id, initial_ban_limit, current_ban_limit, reset_date, username):
        """Met à jour les données du modérateur dans la base de données."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO moderators (user_id, ban_limit, initial_limit, reset_date, username) VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET ban_limit = ?, initial_limit = ?, reset_date = ?, username = ?",
                (user_id, current_ban_limit, initial_ban_limit, reset_date, username, current_ban_limit, initial_ban_limit, reset_date, username)
            )
            conn.commit()
            conn.close()
            logger.info(f"Données mises à jour pour le modérateur {username} (ID: {user_id})")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des données du modérateur {username} (ID: {user_id}): {e}")
            return False
    
    def add_ban_to_history(self, moderator_id, banned_user_id, banned_user_name, reason):
        """Ajoute un bannissement à l'historique."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO ban_history (moderator_id, banned_user_id, banned_user_name, reason) VALUES (?, ?, ?, ?)",
                (moderator_id, banned_user_id, banned_user_name, reason)
            )
            conn.commit()
            conn.close()
            logger.info(f"Bannissement ajouté à l'historique pour {banned_user_name} (ID: {banned_user_id})")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du bannissement: {e}")
            return False
    
    def get_ban_history(self, moderator_id=None):
        """Récupère l'historique des bannissements pour un modérateur spécifique ou tous les bannissements."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if moderator_id:
                cursor.execute(
                    "SELECT * FROM ban_history WHERE moderator_id = ? ORDER BY timestamp DESC",
                    (moderator_id,)
                )
            else:
                cursor.execute("SELECT * FROM ban_history ORDER BY timestamp DESC")
            
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'historique des bannissements: {e}")
            return []
    
    def get_all_ban_history(self):
        """Récupère l'historique de tous les bans depuis la base de données."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ban_history ORDER BY timestamp DESC")
            results = cursor.fetchall()
            conn.close()
            
            return results
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'historique des bans: {e}")
            return []

    def create_moderator(self, user_id, ban_limit, initial_limit, reset_date):
        """Ajoute un modérateur à la base de données."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO moderators (user_id, ban_limit, initial_limit, reset_date) VALUES (?, ?, ?, ?)",
                (user_id, ban_limit, initial_limit, reset_date)
            )
            conn.commit()
            conn.close()
            logger.info(f"Modérateur ajouté: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du modérateur: {e}")
            return False

    def delete_moderator(self, user_id):
        """Supprime un modérateur de la base de données."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM moderators WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            logger.info(f"Modérateur supprimé: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du modérateur: {e}")
            return False

    def delete_ban_history(self, ban_id):
        """Supprime un enregistrement de l'historique des bans."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ban_history WHERE id = ?", (ban_id,))
            conn.commit()
            conn.close()
            logger.info(f"Bannissement supprimé de l'historique: {ban_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'historique des bans: {e}")
            return False

    def get_all_moderators_with_ban_limits(self):
        """Récupère tous les modérateurs et leurs limites de bans."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT username, ban_limit, reset_date FROM moderators")
            results = cursor.fetchall()
            conn.close()
            
            return results
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des modérateurs: {e}")
            return []   