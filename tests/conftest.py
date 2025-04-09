import sys
import os
from dotenv import load_dotenv

# Charger les variables d'environnement avant d'exécuter les tests
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Ajouter le répertoire racine au chemin de recherche
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))