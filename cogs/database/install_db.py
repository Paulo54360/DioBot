import sqlite3
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()



def init_database(db_path="./db/moderation.db"):
    """Initialise la base de données SQLite."""
    try:
        # Vérifier si le fichier existe déjà
        db_exists = os.path.exists(db_path)
        

        
        if db_exists:
            logger.info(f"La base de données {db_path} existe déjà")
        else:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Création des tables
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS moderators (
                user_id INTEGER PRIMARY KEY,
                ban_limit INTEGER,
                initial_limit INTEGER,
                reset_date TEXT
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ban_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                moderator_id INTEGER,
                banned_user_id INTEGER,
                banned_user_name TEXT,
                reason TEXT,
                timestamp TEXT,
                FOREIGN KEY (moderator_id) REFERENCES moderators (user_id)
            )
            ''')

            conn.commit()
            conn.close()
            logger.info(f"Base de données {db_path} créée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")

if __name__ == "__main__":
    # Initialiser la base de données
    init_database()
