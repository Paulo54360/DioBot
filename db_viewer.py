import sqlite3
import os
from tabulate import tabulate  # pip install tabulate

def view_database(db_path):
    """Affiche le contenu des tables de la base de données."""
    if not os.path.exists(db_path):
        print(f"La base de données {db_path} n'existe pas.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Obtenir la liste des tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\n=== Table: {table_name} ===")
        
        # Obtenir les colonnes
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Obtenir les données
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if rows:
            print(tabulate(rows, headers=columns, tablefmt="grid"))
        else:
            print("Aucune donnée")
    
    conn.close()

if __name__ == "__main__":
    db_path = "moderation.db"  # Chemin vers votre base de données
    view_database(db_path) 