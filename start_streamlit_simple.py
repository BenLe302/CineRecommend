#!/usr/bin/env python3
"""
🎬 CineRecommend - Streamlit Launcher
===================================

Script de lancement simple pour l'application Streamlit.

Usage:
    python start_streamlit_simple.py
    
Auteur: Dady Akrou Cyrille
Date: 2024
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Configure l'environnement pour Streamlit."""
    # Ajouter le répertoire racine au PYTHONPATH
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Créer les répertoires nécessaires
    directories = [
        project_root / "logs",
        project_root / "data" / "models",
        project_root / ".streamlit"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Configuration Streamlit
    streamlit_config = project_root / ".streamlit" / "config.toml"
    if not streamlit_config.exists():
        with open(streamlit_config, 'w') as f:
            f.write("""
[server]
port = 8501
address = "0.0.0.0"
maxUploadSize = 200

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[browser]
gatherUsageStats = false
""")

def check_dependencies():
    """Vérifie les dépendances critiques."""
    required_packages = ['streamlit', 'pandas', 'plotly']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.error(f"Packages manquants: {missing}")
        logger.info("Installez avec: pip install -r requirements.txt")
        return False
    
    return True

def launch_streamlit():
    """Lance l'application Streamlit."""
    logger.info("🚀 Lancement de CineRecommend Streamlit...")
    
    # Chemin vers l'application Streamlit
    app_path = Path(__file__).parent / "src" / "streamlit_app" / "app.py"
    
    if not app_path.exists():
        logger.error(f"Application Streamlit non trouvée: {app_path}")
        return False
    
    try:
        # Commande Streamlit
        cmd = [
            "streamlit", "run", str(app_path),
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ]
        
        logger.info(f"Commande: {' '.join(cmd)}")
        logger.info("📱 Application disponible sur: http://localhost:8501")
        logger.info("🛑 Appuyez sur Ctrl+C pour arrêter")
        
        # Lancer Streamlit
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors du lancement: {e}")
        return False
    except KeyboardInterrupt:
        logger.info("🛑 Application arrêtée par l'utilisateur")
        return True
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        return False
    
    return True

def main():
    """Point d'entrée principal."""
    logger.info("🎬 CineRecommend - Démarrage Streamlit")
    logger.info("=" * 40)
    
    # Configuration de l'environnement
    setup_environment()
    
    # Vérification des dépendances
    if not check_dependencies():
        sys.exit(1)
    
    # Lancement de Streamlit
    success = launch_streamlit()
    
    if success:
        logger.info("✅ Application fermée proprement")
    else:
        logger.error("❌ Erreur lors du lancement")
        sys.exit(1)

if __name__ == "__main__":
    main()