import sqlite3
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def init_database(db_path="moderation.db"):
    """Initialise la base de données SQLite."""
    try:
        # Vérifier si le fichier existe déjà
        db_exists = os.path.exists(db_path)
        
        # Connexion à la base de données
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
        
        if db_exists:
            logger.info(f"Base de données {db_path} mise à jour avec succès")
        else:
            logger.info(f"Base de données {db_path} créée avec succès")
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        return False

if __name__ == "__main__":
    # Initialiser la base de données
    success = init_database()
    
    if success:
        # Vérifier que les tables ont été créées
        conn = sqlite3.connect("moderation.db")
        cursor = conn.cursor()
        
        # Lister les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if tables:
            logger.info("Tables créées :")
            for table in tables:
                logger.info(f"- {table[0]}")
        else:
            logger.warning("Aucune table n'a été créée !")
        
        conn.close() 