#!/usr/bin/env python3
"""
🎬 CineRecommend - Project Launcher
==================================

Script de lancement ultra-rapide pour CineRecommend.
Ce script configure tout automatiquement en 1 minute.

Usage:
    python launch_project.py
    
Auteur: Dady Akrou Cyrille
Date: 2024
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor
import threading

# Configuration du logging avec couleurs
class ColoredFormatter(logging.Formatter):
    """Formatter avec couleurs pour les logs."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Vert
        'WARNING': '\033[33m',  # Jaune
        'ERROR': '\033[31m',    # Rouge
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)

# Configuration du logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))
logger.addHandler(handler)

class ProjectLauncher:
    """Lanceur de projet ultra-rapide."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.start_time = time.time()
        
    def print_banner(self):
        """Affiche la bannière du projet."""
        banner = """
🎬 ═══════════════════════════════════════════════════════════════
   ██████╗██╗███╗   ██╗███████╗██████╗ ███████╗ ██████╗ ██████╗ 
  ██╔════╝██║████╗  ██║██╔════╝██╔══██╗██╔════╝██╔════╝██╔═══██╗
  ██║     ██║██╔██╗ ██║█████╗  ██████╔╝█████╗  ██║     ██║   ██║
  ██║     ██║██║╚██╗██║██╔══╝  ██╔══██╗██╔══╝  ██║     ██║   ██║
  ╚██████╗██║██║ ╚████║███████╗██║  ██║███████╗╚██████╗╚██████╔╝
   ╚═════╝╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ 
                                                                 
   🎯 Système de Recommandation de Films Intelligent
   🚀 Lancement Ultra-Rapide (< 1 minute)
   ⚡ Powered by FastAPI + Streamlit + ML
═══════════════════════════════════════════════════════════════ 🎬
"""
        print(banner)
        logger.info("🎬 Initialisation de CineRecommend...")
    
    def quick_setup(self):
        """Configuration rapide de l'environnement."""
        logger.info("⚡ Configuration express...")
        
        # Créer les répertoires essentiels
        essential_dirs = [
            "data/models", "data/processed", "logs", ".streamlit"
        ]
        
        for dir_path in essential_dirs:
            (self.project_root / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Configuration Streamlit minimale
        streamlit_config = self.project_root / ".streamlit" / "config.toml"
        if not streamlit_config.exists():
            with open(streamlit_config, 'w') as f:
                f.write("""
[server]
port = 8501
address = "0.0.0.0"

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"

[browser]
gatherUsageStats = false
""")
        
        logger.info("✅ Configuration terminée")
    
    def check_critical_files(self):
        """Vérifie les fichiers critiques."""
        logger.info("🔍 Vérification des fichiers...")
        
        critical_files = [
            "src/streamlit_app/app.py",
            "data/processed/movies_sample.csv",
            "data/processed/ratings_sample.csv"
        ]
        
        missing = []
        for file_path in critical_files:
            if not (self.project_root / file_path).exists():
                missing.append(file_path)
        
        if missing:
            logger.error(f"❌ Fichiers manquants: {missing}")
            return False
        
        logger.info("✅ Tous les fichiers critiques présents")
        return True
    
    def install_dependencies(self):
        """Installation rapide des dépendances critiques."""
        logger.info("📦 Vérification des dépendances...")
        
        critical_packages = {
            'streamlit': 'streamlit>=1.28.0',
            'pandas': 'pandas>=2.0.0',
            'plotly': 'plotly>=5.0.0',
            'scikit-learn': 'scikit-learn>=1.3.0'
        }
        
        missing = []
        for package, version in critical_packages.items():
            try:
                __import__(package)
                logger.info(f"✅ {package}")
            except ImportError:
                missing.append(version)
        
        if missing:
            logger.info(f"📦 Installation de {len(missing)} packages...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "--quiet"
                ] + missing, check=True)
                logger.info("✅ Dépendances installées")
            except subprocess.CalledProcessError:
                logger.warning("⚠️  Erreur d'installation, continuons...")
        else:
            logger.info("✅ Toutes les dépendances présentes")
    
    def prepare_models(self):
        """Préparation rapide des modèles."""
        logger.info("🤖 Préparation des modèles...")
        
        try:
            # Import et préparation minimale
            sys.path.append(str(self.project_root))
            
            # Vérifier si les modèles existent déjà
            model_files = [
                "data/models/collaborative/cf_model.pkl",
                "data/models/content_based/cb_model.pkl"
            ]
            
            models_exist = all(
                (self.project_root / model_file).exists() 
                for model_file in model_files
            )
            
            if models_exist:
                logger.info("✅ Modèles déjà présents")
                return True
            
            # Entraînement rapide si nécessaire
            logger.info("🔄 Entraînement express des modèles...")
            
            # Ici on pourrait ajouter un entraînement rapide
            # Pour l'instant, on continue sans modèles
            logger.info("ℹ️  Mode démo sans modèles pré-entraînés")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️  Erreur modèles: {e}")
            return True  # Continue quand même
    
    def launch_application(self):
        """Lance l'application Streamlit."""
        elapsed = time.time() - self.start_time
        logger.info(f"🚀 Lancement de l'application (temps: {elapsed:.1f}s)")
        
        app_path = self.project_root / "src" / "streamlit_app" / "app.py"
        
        if not app_path.exists():
            logger.error(f"❌ Application non trouvée: {app_path}")
            return False
        
        try:
            logger.info("🌟 CineRecommend est prêt!")
            logger.info("📱 Ouverture dans le navigateur...")
            logger.info("🔗 URL: http://localhost:8501")
            logger.info("🛑 Ctrl+C pour arrêter")
            print("\n" + "="*50)
            
            # Lancer Streamlit
            subprocess.run([
                "streamlit", "run", str(app_path),
                "--server.port", "8501",
                "--server.address", "0.0.0.0",
                "--browser.gatherUsageStats", "false"
            ])
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Application arrêtée")
        except Exception as e:
            logger.error(f"❌ Erreur: {e}")
            return False
        
        return True
    
    def run(self):
        """Exécute le lancement complet."""
        try:
            # Bannière
            self.print_banner()
            
            # Configuration rapide
            self.quick_setup()
            
            # Vérifications
            if not self.check_critical_files():
                logger.error("❌ Fichiers critiques manquants")
                return False
            
            # Dépendances
            self.install_dependencies()
            
            # Modèles
            self.prepare_models()
            
            # Lancement
            return self.launch_application()
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Arrêt demandé")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur fatale: {e}")
            return False

def main():
    """Point d'entrée principal."""
    launcher = ProjectLauncher()
    success = launcher.run()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()