#!/usr/bin/env python3
"""
🎬 CineRecommend - Application Streamlit
======================================

Interface utilisateur principale pour le système de recommandation de films.

Auteur: Dady Akrou Cyrille
Date: 2024
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import sys
import os
from pathlib import Path
import logging
import time
from typing import List, Dict, Optional
import requests
import json

# Configuration de la page
st.set_page_config(
    page_title="🎬 CineRecommend",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .movie-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f9f9f9;
    }
    
    .recommendation-score {
        background: #FF6B6B;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

class CineRecommendApp:
    """Application principale CineRecommend."""
    
    def __init__(self):
        self.project_root = project_root
        self.data_dir = self.project_root / "data"
        self.processed_dir = self.data_dir / "processed"
        
        # Initialiser les données
        self.movies_df = None
        self.ratings_df = None
        self.load_data()
    
    def load_data(self):
        """Charge les données de films et d'évaluations."""
        try:
            # Charger les données d'exemple
            movies_file = self.processed_dir / "movies_sample.csv"
            ratings_file = self.processed_dir / "ratings_sample.csv"
            
            if movies_file.exists() and ratings_file.exists():
                self.movies_df = pd.read_csv(movies_file)
                self.ratings_df = pd.read_csv(ratings_file)
                logger.info(f"Données chargées: {len(self.movies_df)} films, {len(self.ratings_df)} évaluations")
            else:
                # Créer des données d'exemple si les fichiers n'existent pas
                self.create_sample_data()
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données: {e}")
            self.create_sample_data()
    
    def create_sample_data(self):
        """Crée des données d'exemple pour la démonstration."""
        # Films d'exemple
        sample_movies = {
            'movieId': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'title': [
                'Toy Story (1995)',
                'Jumanji (1995)',
                'Grumpier Old Men (1995)',
                'Waiting to Exhale (1995)',
                'Father of the Bride Part II (1995)',
                'Heat (1995)',
                'Sabrina (1995)',
                'Tom and Huck (1995)',
                'Sudden Death (1995)',
                'GoldenEye (1995)'
            ],
            'genres': [
                'Adventure|Animation|Children|Comedy|Fantasy',
                'Adventure|Children|Fantasy',
                'Comedy|Romance',
                'Comedy|Drama|Romance',
                'Comedy',
                'Action|Crime|Thriller',
                'Comedy|Romance',
                'Adventure|Children',
                'Action',
                'Action|Adventure|Thriller'
            ]
        }
        
        # Évaluations d'exemple
        sample_ratings = {
            'userId': [1, 1, 1, 2, 2, 3, 3, 4, 4, 5] * 10,
            'movieId': [1, 2, 3, 1, 4, 2, 5, 1, 3, 2] * 10,
            'rating': [4.0, 3.5, 5.0, 4.5, 3.0, 4.0, 2.5, 5.0, 3.5, 4.0] * 10,
            'timestamp': [964982703] * 100
        }
        
        self.movies_df = pd.DataFrame(sample_movies)
        self.ratings_df = pd.DataFrame(sample_ratings)
        
        logger.info("Données d'exemple créées")
    
    def get_movie_stats(self):
        """Calcule les statistiques des films."""
        if self.movies_df is None or self.ratings_df is None:
            return {}
        
        # Fusionner les données
        merged_df = self.ratings_df.merge(self.movies_df, on='movieId')
        
        stats = {
            'total_movies': len(self.movies_df),
            'total_ratings': len(self.ratings_df),
            'total_users': self.ratings_df['userId'].nunique(),
            'avg_rating': self.ratings_df['rating'].mean(),
            'top_rated_movie': merged_df.groupby('title')['rating'].mean().idxmax(),
            'most_rated_movie': merged_df['title'].value_counts().index[0]
        }
        
        return stats
    
    def get_recommendations(self, user_id: int = None, movie_title: str = None, n_recommendations: int = 5):
        """Génère des recommandations (simulation)."""
        if self.movies_df is None:
            return []
        
        # Simulation de recommandations
        sample_movies = self.movies_df.sample(min(n_recommendations, len(self.movies_df)))
        
        recommendations = []
        for _, movie in sample_movies.iterrows():
            recommendations.append({
                'title': movie['title'],
                'genres': movie['genres'],
                'score': np.random.uniform(0.7, 0.95),
                'reason': 'Basé sur vos préférences'
            })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)
    
    def search_movies(self, query: str):
        """Recherche des films par titre."""
        if self.movies_df is None or not query:
            return []
        
        # Recherche insensible à la casse
        mask = self.movies_df['title'].str.contains(query, case=False, na=False)
        results = self.movies_df[mask]
        
        return results.to_dict('records')
    
    def get_genre_distribution(self):
        """Analyse la distribution des genres."""
        if self.movies_df is None:
            return {}
        
        # Extraire tous les genres
        all_genres = []
        for genres_str in self.movies_df['genres'].dropna():
            genres = genres_str.split('|')
            all_genres.extend(genres)
        
        # Compter les occurrences
        genre_counts = pd.Series(all_genres).value_counts()
        
        return genre_counts.to_dict()
    
    def get_rating_distribution(self):
        """Analyse la distribution des notes."""
        if self.ratings_df is None:
            return {}
        
        return self.ratings_df['rating'].value_counts().sort_index().to_dict()

def main():
    """Fonction principale de l'application."""
    
    # Initialiser l'application
    app = CineRecommendApp()
    
    # En-tête principal
    st.markdown('<h1 class="main-header">🎬 CineRecommend</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Système de Recommandation de Films Intelligent</p>', unsafe_allow_html=True)
    
    # Sidebar pour la navigation
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.selectbox(
        "Choisir une page",
        ["🏠 Accueil", "🎬 Recommandations", "🔍 Recherche", "📊 Analytics", "👤 Profil"]
    )
    
    # Page d'accueil
    if page == "🏠 Accueil":
        st.header("📊 Tableau de Bord")
        
        # Statistiques principales
        stats = app.get_movie_stats()
        
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🎬 Films", f"{stats['total_movies']:,}")
            
            with col2:
                st.metric("⭐ Évaluations", f"{stats['total_ratings']:,}")
            
            with col3:
                st.metric("👥 Utilisateurs", f"{stats['total_users']:,}")
            
            with col4:
                st.metric("📈 Note Moyenne", f"{stats['avg_rating']:.1f}/5")
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Distribution des Genres")
            genre_dist = app.get_genre_distribution()
            if genre_dist:
                fig = px.bar(
                    x=list(genre_dist.keys())[:10],
                    y=list(genre_dist.values())[:10],
                    title="Top 10 des Genres"
                )
                fig.update_layout(xaxis_title="Genre", yaxis_title="Nombre de Films")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("⭐ Distribution des Notes")
            rating_dist = app.get_rating_distribution()
            if rating_dist:
                fig = px.pie(
                    values=list(rating_dist.values()),
                    names=list(rating_dist.keys()),
                    title="Répartition des Notes"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Page des recommandations
    elif page == "🎬 Recommandations":
        st.header("🎯 Recommandations Personnalisées")
        
        # Paramètres de recommandation
        col1, col2 = st.columns([2, 1])
        
        with col1:
            user_id = st.number_input("ID Utilisateur", min_value=1, max_value=1000, value=1)
        
        with col2:
            n_recs = st.slider("Nombre de recommandations", 1, 20, 10)
        
        if st.button("🚀 Générer des Recommandations"):
            with st.spinner("Génération des recommandations..."):
                recommendations = app.get_recommendations(user_id=user_id, n_recommendations=n_recs)
                
                if recommendations:
                    st.success(f"✅ {len(recommendations)} recommandations générées!")
                    
                    for i, rec in enumerate(recommendations, 1):
                        with st.container():
                            col1, col2, col3 = st.columns([3, 1, 1])
                            
                            with col1:
                                st.write(f"**{i}. {rec['title']}**")
                                st.write(f"*Genres: {rec['genres']}*")
                                st.write(f"💡 {rec['reason']}")
                            
                            with col2:
                                st.markdown(f'<div class="recommendation-score">Score: {rec["score"]:.2f}</div>', unsafe_allow_html=True)
                            
                            with col3:
                                if st.button(f"👍", key=f"like_{i}"):
                                    st.success("Merci pour votre feedback!")
                            
                            st.divider()
                else:
                    st.warning("Aucune recommandation disponible.")
    
    # Page de recherche
    elif page == "🔍 Recherche":
        st.header("🔍 Recherche de Films")
        
        # Barre de recherche
        search_query = st.text_input("🎬 Rechercher un film...", placeholder="Ex: Toy Story")
        
        if search_query:
            results = app.search_movies(search_query)
            
            if results:
                st.success(f"✅ {len(results)} film(s) trouvé(s)")
                
                for movie in results:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**{movie['title']}**")
                            st.write(f"*Genres: {movie['genres']}*")
                        
                        with col2:
                            if st.button(f"➕ Ajouter aux favoris", key=f"fav_{movie['movieId']}"):
                                st.success("Ajouté aux favoris!")
                        
                        st.divider()
            else:
                st.info("Aucun film trouvé pour cette recherche.")
        
        # Filtres avancés
        with st.expander("🔧 Filtres Avancés"):
            col1, col2 = st.columns(2)
            
            with col1:
                genre_filter = st.selectbox(
                    "Genre",
                    ["Tous"] + list(app.get_genre_distribution().keys())[:10]
                )
            
            with col2:
                year_filter = st.slider("Année", 1990, 2024, (2000, 2024))
    
    # Page d'analytics
    elif page == "📊 Analytics":
        st.header("📊 Analytics et Insights")
        
        # Métriques avancées
        stats = app.get_movie_stats()
        
        if stats:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏆 Top Performances")
                st.write(f"**Film le mieux noté:** {stats.get('top_rated_movie', 'N/A')}")
                st.write(f"**Film le plus évalué:** {stats.get('most_rated_movie', 'N/A')}")
            
            with col2:
                st.subheader("📈 Tendances")
                st.write("**Croissance des évaluations:** +15% ce mois")
                st.write("**Nouveaux utilisateurs:** +8% cette semaine")
        
        # Graphiques avancés
        st.subheader("📊 Visualisations Avancées")
        
        # Simulation de données temporelles
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        values = np.random.randint(50, 200, 30)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name='Évaluations par jour',
            line=dict(color='#FF6B6B', width=3)
        ))
        
        fig.update_layout(
            title="Évolution des Évaluations (30 derniers jours)",
            xaxis_title="Date",
            yaxis_title="Nombre d'évaluations"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Page de profil
    elif page == "👤 Profil":
        st.header("👤 Profil Utilisateur")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image("https://via.placeholder.com/150x150/FF6B6B/FFFFFF?text=User", width=150)
            st.write("**Utilisateur #1**")
            st.write("📅 Membre depuis: Janvier 2024")
            st.write("⭐ Films évalués: 42")
            st.write("🎯 Recommandations reçues: 156")
        
        with col2:
            st.subheader("🎬 Historique des Films")
            
            # Simulation d'historique
            history_data = {
                'Film': ['Toy Story', 'Jumanji', 'Heat', 'GoldenEye'],
                'Note': [4.5, 3.5, 5.0, 4.0],
                'Date': ['2024-01-15', '2024-01-10', '2024-01-05', '2024-01-01']
            }
            
            history_df = pd.DataFrame(history_data)
            st.dataframe(history_df, use_container_width=True)
            
            st.subheader("📊 Vos Préférences")
            
            # Graphique des préférences par genre
            pref_data = {
                'Genre': ['Action', 'Comedy', 'Drama', 'Sci-Fi'],
                'Score': [4.2, 3.8, 4.5, 4.0]
            }
            
            fig = px.bar(
                x=pref_data['Genre'],
                y=pref_data['Score'],
                title="Vos Préférences par Genre",
                color=pref_data['Score'],
                color_continuous_scale='Viridis'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666;">'
        '🎬 CineRecommend - Développé avec ❤️ par Dady Akrou Cyrille | '
        '<a href="https://github.com/BenLe302/CineRecommend" target="_blank">GitHub</a>'
        '</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()