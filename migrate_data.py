import json
import sqlite3
from datetime import datetime
import logging
import os

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def migrate_json_to_sqlite(json_path="banData.json", db_path="moderation.db"):
    """Migre les données du fichier JSON vers la base de données SQLite."""
    try:
        # Vérifier si le fichier JSON existe
        if not os.path.exists(json_path):
            logger.warning(f"Le fichier {json_path} n'existe pas.")
            return False
        
        # Vérifier si la base de données existe
        if not os.path.exists(db_path):
            logger.warning(f"La base de données {db_path} n'existe pas.")
            return False
        
        # Charger les données JSON
        with open(json_path, 'r') as f:
            content = f.read().strip()
            if not content:
                logger.warning("Le fichier JSON est vide.")
                return False
            ban_data = json.loads(content)
        
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Migrer les données des modérateurs
        moderators_count = 0
        for mod_id, mod_data in ban_data.get("moderators", {}).items():
            # Vérifier si les données nécessaires sont présentes
            if all(key in mod_data for key in ["limit", "initial_limit", "time_reset"]):
                # Insérer ou mettre à jour le modérateur
                cursor.execute(
                    "INSERT OR REPLACE INTO moderators (user_id, ban_limit, initial_limit, reset_date) VALUES (?, ?, ?, ?)",
                    (int(mod_id), mod_data["limit"], mod_data["initial_limit"], mod_data["time_reset"])
                )
                moderators_count += 1
        
        conn.commit()
        conn.close()
        
        logger.info(f"Migration terminée : {moderators_count} modérateurs migrés.")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la migration : {e}")
        return False

if __name__ == "__main__":
    # Initialiser la base de données (au cas où)
    import init_db
    init_db.init_database()
    
    # Migrer les données
    migrate_json_to_sqlite()
    
    # Vérifier les données migrées
    conn = sqlite3.connect("moderation.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM moderators")
    mod_count = cursor.fetchone()[0]
    
    logger.info(f"Nombre de modérateurs dans la base de données : {mod_count}")
    
    conn.close() 