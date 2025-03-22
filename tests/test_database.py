import unittest
import sqlite3
import os
from datetime import datetime, timedelta
from cogs.moderation.database import ModerationDB

class TestModerationDB(unittest.TestCase):
    """Tests pour la classe ModerationDB."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        # Utiliser un fichier temporaire pour la base de données
        self.db_path = "test_moderation.db"
        self.db = ModerationDB(self.db_path)
        
        # Initialiser la base de données
        self.db.init_database()
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        # Supprimer le fichier de base de données temporaire
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_set_moderator_data(self):
        """Test de la méthode set_moderator_data."""
        # Données de test
        user_id = 123456789
        ban_limit = 5
        initial_limit = 10
        reset_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
        
        # Appel de la méthode à tester
        success = self.db.set_moderator_data(user_id, ban_limit, initial_limit, reset_date)
        
        # Vérification du résultat
        self.assertTrue(success)
        
        # Vérification des données en base
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT ban_limit, initial_limit, reset_date FROM moderators WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], ban_limit)
        self.assertEqual(result[1], initial_limit)
        self.assertEqual(result[2], reset_date)
    
    def test_get_moderator_data(self):
        """Test de la méthode get_moderator_data."""
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
        
        # Appel de la méthode à tester
        result = self.db.get_moderator_data(user_id)
        
        # Vérification du résultat
        self.assertIsNotNone(result)
        self.assertEqual(result["user_id"], user_id)
        self.assertEqual(result["ban_limit"], ban_limit)
        self.assertEqual(result["initial_limit"], initial_limit)
        self.assertEqual(result["reset_date"], reset_date)
    
    def test_add_ban_history(self):
        """Test de la méthode add_ban_history."""
        # Données de test
        mod_id = 123456789
        banned_id = 987654321
        banned_name = "TestUser"
        reason = "Test reason"
        
        # Appel de la méthode à tester
        success = self.db.add_ban_history(mod_id, banned_id, banned_name, reason)
        
        # Vérification du résultat
        self.assertTrue(success)
        
        # Vérification des données en base
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT mod_id, banned_id, banned_name, reason FROM ban_history WHERE mod_id = ?", (mod_id,))
        result = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], mod_id)
        self.assertEqual(result[1], banned_id)
        self.assertEqual(result[2], banned_name)
        self.assertEqual(result[3], reason)
    
    # Ajoutez d'autres tests pour les méthodes restantes...

if __name__ == "__main__":
    unittest.main() 