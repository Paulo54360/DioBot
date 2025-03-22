import sqlite3
import os
import logging
from datetime import datetime

logger = logging.getLogger("moderation")

class ModerationDB:
    """Gère les interactions avec la base de données pour le module de modération."""
    
    def __init__(self, db_path):
        self.db_path = db_path
    
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
                reset_date TEXT
            )
            ''')
            
            # Créer la table de l'historique des bans
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ban_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mod_id INTEGER,
                banned_id INTEGER,
                banned_name TEXT,
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
                    "reset_date": result[3]
                }
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données du modérateur: {e}")
            return None
    
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
                    "reset_date": result[3]
                })
            return moderators
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de tous les modérateurs: {e}")
            return []
    
    def set_moderator_data(self, user_id, ban_limit, initial_limit, reset_date):
        """Définit ou met à jour les données d'un modérateur dans la base de données."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Vérifier si le modérateur existe déjà
            cursor.execute("SELECT * FROM moderators WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                # Mettre à jour les données existantes
                cursor.execute(
                    "UPDATE moderators SET ban_limit = ?, initial_limit = ?, reset_date = ? WHERE user_id = ?",
                    (ban_limit, initial_limit, reset_date, user_id)
                )
            else:
                # Insérer un nouveau modérateur
                cursor.execute(
                    "INSERT INTO moderators (user_id, ban_limit, initial_limit, reset_date) VALUES (?, ?, ?, ?)",
                    (user_id, ban_limit, initial_limit, reset_date)
                )
            
            conn.commit()
            conn.close()
            logger.info(f"Données du modérateur {user_id} mises à jour avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des données du modérateur: {e}")
            return False
    
    def add_ban_history(self, mod_id, banned_id, banned_name, reason):
        """Ajoute un bannissement à l'historique."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO ban_history (mod_id, banned_id, banned_name, reason) VALUES (?, ?, ?, ?)",
                (mod_id, banned_id, banned_name, reason)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du bannissement: {e}")
            return False
    
    def get_ban_history(self, moderator_id=None, limit=10):
        """Récupère l'historique des bannissements."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if moderator_id:
                cursor.execute(
                    "SELECT * FROM ban_history WHERE moderator_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (moderator_id, limit)
                )
            else:
                cursor.execute("SELECT * FROM ban_history ORDER BY timestamp DESC LIMIT ?", (limit,))
            
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'historique des bannissements: {e}")
            return [] 