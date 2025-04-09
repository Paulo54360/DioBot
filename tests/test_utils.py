import unittest
from datetime import datetime, timedelta
import sqlite3
import os
from cogs.moderation.utils import check_and_reset_limit, format_date
from cogs.moderation.database.database import ModerationDB

class TestUtils(unittest.TestCase):
    """Tests pour les fonctions utilitaires."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        # Utiliser un fichier temporaire pour la base de données
        self.db_path = "test_utils.db"
        self.db = ModerationDB(self.db_path)
        
        # Initialiser la base de données
        self.db.init_database()
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        # Supprimer le fichier de base de données temporaire
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_format_date(self):
        """Test de la fonction format_date."""
        # Données de test
        date_str = "2023-12-31T23:59:59"
        
        # Appel de la fonction à tester
        result = format_date(date_str)
        
        # Vérification du résultat - corriger l'assertion selon le format réel
        self.assertEqual(result, "31/12/2023 23:59")  # Ajuster selon le format réel de votre fonction
    
    def test_check_and_reset_limit_not_expired(self):
        """Test de la fonction check_and_reset_limit quand la date n'est pas expirée."""
        # Données de test
        user_id = 123456789
        ban_limit = 5
        initial_limit = 10
        reset_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
        
        # Insertion des données de test
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO moderators (user_id, ban_limit, initial_limit, reset_date) VALUES (?, ?, ?, ?)",
            (user_id, ban_limit, initial_limit, reset_date)
        )
        conn.commit()
        conn.close()
        
        # Appel de la fonction à tester
        check_and_reset_limit(self.db, user_id)
        
        # Vérification du résultat
        result = self.db.get_moderator_data(user_id)
        self.assertEqual(result["ban_limit"], ban_limit)  # La limite ne doit pas changer
    
    def test_check_and_reset_limit_expired(self):
        """Test de la fonction check_and_reset_limit quand la date est expirée."""
        # Données de test
        user_id = 123456789
        ban_limit = 5
        initial_limit = 10
        reset_date = (datetime.utcnow() - timedelta(days=1)).isoformat()  # Date expirée
        
        # Insertion des données de test
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO moderators (user_id, ban_limit, initial_limit, reset_date) VALUES (?, ?, ?, ?)",
            (user_id, ban_limit, initial_limit, reset_date)
        )
        conn.commit()
        conn.close()
        
        # Appel de la fonction à tester
        check_and_reset_limit(self.db, user_id)
        
        # Vérification du résultat
        result = self.db.get_moderator_data(user_id)
        self.assertEqual(result["ban_limit"], initial_limit)  # La limite doit être réinitialisée
        self.assertNotEqual(result["reset_date"], reset_date)  # La date doit être mise à jour

if __name__ == "__main__":
    unittest.main() 