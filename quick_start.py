#!/usr/bin/env python3
"""
🎬 CineRecommend - Quick Start Script
====================================

Script de démarrage rapide pour le système de recommandation de films.
Ce script configure automatiquement l'environnement et lance le pipeline complet.

Usage:
    python quick_start.py
    
Auteur: Dady Akrou Cyrille
Date: 2024
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import logging
from typing import Optional

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/quick_start.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class QuickStart:
    """Gestionnaire de démarrage rapide pour CineRecommend."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.models_dir = self.data_dir / "models"
        self.processed_dir = self.data_dir / "processed"
        
    def check_dependencies(self) -> bool:
        """Vérifie que toutes les dépendances sont installées."""
        logger.info("🔍 Vérification des dépendances...")
        
        required_packages = [
            'pandas', 'numpy', 'scikit-learn', 'surprise',
            'fastapi', 'uvicorn', 'streamlit', 'plotly'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"✅ {package} installé")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"❌ {package} manquant")
        
        if missing_packages:
            logger.error(f"Packages manquants: {missing_packages}")
            logger.info("Installez avec: pip install -r requirements.txt")
            return False
        
        logger.info("✅ Toutes les dépendances sont installées")
        return True
    
    def setup_directories(self) -> None:
        """Crée les répertoires nécessaires."""
        logger.info("📁 Configuration des répertoires...")
        
        directories = [
            self.data_dir / "raw",
            self.data_dir / "processed",
            self.data_dir / "models" / "collaborative",
            self.data_dir / "models" / "content_based",
            self.data_dir / "models" / "hybrid",
            self.project_root / "logs",
            self.project_root / "results"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Créé: {directory}")
    
    def check_data_files(self) -> bool:
        """Vérifie la présence des fichiers de données."""
        logger.info("📊 Vérification des fichiers de données...")
        
        # Fichiers requis
        required_files = [
            "data/processed/movies_sample.csv",
            "data/processed/ratings_sample.csv"
        ]
        
        # Fichiers optionnels (dataset complet)
        optional_files = [
            "Dataset/movies.csv",
            "Dataset/ratings.csv"
        ]
        
        # Vérifier les fichiers requis
        missing_required = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                logger.info(f"✅ Trouvé: {file_path}")
            else:
                missing_required.append(file_path)
                logger.warning(f"❌ Manquant: {file_path}")
        
        # Vérifier les fichiers optionnels
        for file_path in optional_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                logger.info(f"✅ Dataset complet trouvé: {file_path}")
            else:
                logger.info(f"ℹ️  Dataset complet non trouvé: {file_path}")
        
        if missing_required:
            logger.error(f"Fichiers de données requis manquants: {missing_required}")
            return False
        
        return True
    
    def run_data_pipeline(self) -> bool:
        """Exécute le pipeline de traitement des données."""
        logger.info("🔄 Lancement du pipeline de données...")
        
        try:
            # Import des modules nécessaires
            sys.path.append(str(self.project_root))
            
            from src.data_processing.preprocess import DataProcessor
            from src.models.collaborative_filtering_simple import CollaborativeFilteringSimple
            from src.models.content_based_filtering import ContentBasedFiltering
            from src.models.hybrid_system import HybridRecommender
            
            # Traitement des données
            logger.info("📊 Traitement des données...")
            processor = DataProcessor()
            
            # Charger les données
            movies_file = self.project_root / "data/processed/movies_sample.csv"
            ratings_file = self.project_root / "data/processed/ratings_sample.csv"
            
            if not movies_file.exists() or not ratings_file.exists():
                logger.error("Fichiers de données manquants")
                return False
            
            movies_df, ratings_df = processor.load_data(
                str(movies_file), str(ratings_file)
            )
            
            # Préprocessing
            movies_processed = processor.preprocess_movies(movies_df)
            ratings_processed = processor.preprocess_ratings(ratings_df)
            
            logger.info(f"📊 Films traités: {len(movies_processed)}")
            logger.info(f"📊 Évaluations traitées: {len(ratings_processed)}")
            
            # Entraînement des modèles
            logger.info("🤖 Entraînement des modèles...")
            
            # Modèle collaboratif
            logger.info("🤝 Entraînement du modèle collaboratif...")
            cf_model = CollaborativeFilteringSimple()
            cf_model.fit(ratings_processed)
            cf_model.save_model(str(self.models_dir / "collaborative" / "cf_model.pkl"))
            
            # Modèle basé sur le contenu
            logger.info("📝 Entraînement du modèle basé sur le contenu...")
            cb_model = ContentBasedFiltering()
            cb_model.fit(movies_processed)
            cb_model.save_model(str(self.models_dir / "content_based" / "cb_model.pkl"))
            
            # Modèle hybride
            logger.info("🔄 Création du modèle hybride...")
            hybrid_model = HybridRecommender()
            hybrid_model.fit(movies_processed, ratings_processed)
            hybrid_model.save_model(str(self.models_dir / "hybrid" / "hybrid_model.pkl"))
            
            logger.info("✅ Pipeline de données terminé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur dans le pipeline: {str(e)}")
            return False
    
    def test_api(self) -> bool:
        """Teste l'API FastAPI."""
        logger.info("🧪 Test de l'API...")
        
        try:
            # Démarrer l'API en arrière-plan
            api_process = subprocess.Popen([
                sys.executable, "start_api_simple.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Attendre que l'API démarre
            time.sleep(5)
            
            # Tester l'API
            import requests
            response = requests.get("http://localhost:8000/health")
            
            if response.status_code == 200:
                logger.info("✅ API fonctionne correctement")
                api_process.terminate()
                return True
            else:
                logger.error(f"❌ API erreur: {response.status_code}")
                api_process.terminate()
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur test API: {str(e)}")
            return False
    
    def launch_streamlit(self) -> None:
        """Lance l'application Streamlit."""
        logger.info("🚀 Lancement de l'application Streamlit...")
        
        try:
            # Lancer Streamlit
            subprocess.run([
                sys.executable, "start_streamlit_simple.py"
            ])
        except KeyboardInterrupt:
            logger.info("🛑 Application arrêtée par l'utilisateur")
        except Exception as e:
            logger.error(f"❌ Erreur Streamlit: {str(e)}")
    
    def run(self) -> None:
        """Exécute le processus de démarrage rapide complet."""
        logger.info("🎬 Démarrage de CineRecommend...")
        logger.info("=" * 50)
        
        # Étape 1: Vérifier les dépendances
        if not self.check_dependencies():
            logger.error("❌ Échec: dépendances manquantes")
            return
        
        # Étape 2: Configurer les répertoires
        self.setup_directories()
        
        # Étape 3: Vérifier les données
        if not self.check_data_files():
            logger.error("❌ Échec: fichiers de données manquants")
            return
        
        # Étape 4: Exécuter le pipeline
        if not self.run_data_pipeline():
            logger.error("❌ Échec: pipeline de données")
            return
        
        # Étape 5: Tester l'API (optionnel)
        # self.test_api()
        
        # Étape 6: Lancer Streamlit
        logger.info("🎉 Configuration terminée avec succès!")
        logger.info("🚀 Lancement de l'application...")
        logger.info("📱 L'application sera disponible sur: http://localhost:8501")
        logger.info("=" * 50)
        
        self.launch_streamlit()

def main():
    """Point d'entrée principal."""
    try:
        quick_start = QuickStart()
        quick_start.run()
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()