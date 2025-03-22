import sqlite3
from datetime import datetime, timedelta

# Connexion à la base de données
conn = sqlite3.connect("moderation.db")
cursor = conn.cursor()

# ID Discord d'un modérateur de test (remplacez par un ID réel)
test_mod_id = 123456789012345678

# Date de réinitialisation (30 jours à partir de maintenant)
reset_date = (datetime.utcnow() + timedelta(days=30)).isoformat()

# Ajouter le modérateur de test
cursor.execute(
    "INSERT OR REPLACE INTO moderators (user_id, ban_limit, initial_limit, reset_date) VALUES (?, ?, ?, ?)",
    (test_mod_id, 10, 10, reset_date)
)

conn.commit()
conn.close()

print(f"Modérateur de test ajouté avec l'ID {test_mod_id}") 