from datetime import datetime, timedelta
import logging

logger = logging.getLogger("moderation")

def check_and_reset_limit(db, user_id):
    """Vérifie si la limite de bans doit être réinitialisée et le fait si nécessaire."""
    try:
        mod_data = db.get_moderator_data(user_id)
        if not mod_data:
            return False
        
        # Convertir les dates en objets datetime
        current_date = datetime.utcnow()
        reset_date = datetime.fromisoformat(mod_data["reset_date"])
        
        # Si la date de réinitialisation est dépassée
        if current_date >= reset_date:
            # Calculer la nouvelle date de réinitialisation (même intervalle que précédemment)
            days_interval = (reset_date - (reset_date - timedelta(days=30))).days
            new_reset_date = current_date + timedelta(days=days_interval)
            
            # Mettre à jour les données
            db.set_moderator_data(
                user_id,
                mod_data["initial_limit"],
                mod_data["initial_limit"],
                new_reset_date.isoformat()
            )
            logger.info(f"Limite de bans réinitialisée pour l'utilisateur {user_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la vérification/réinitialisation de la limite: {e}")
        return False

def format_date(date_str):
    """Formate une date ISO en format lisible."""
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime("%d/%m/%Y %H:%M")
    except Exception as e:
        logger.error(f"Erreur lors du formatage de la date: {e}")
        return date_str 