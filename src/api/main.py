#!/usr/bin/env python3
"""
🎬 CineRecommend - API FastAPI
=============================

API REST pour le système de recommandation de films.

Auteur: Dady Akrou Cyrille
Date: 2024
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path as PathLib
import logging
import time
from datetime import datetime
import uvicorn

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajouter le répertoire racine au path
project_root = PathLib(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Modèles Pydantic
class Movie(BaseModel):
    """Modèle pour un film."""
    movieId: int
    title: str
    genres: str
    year: Optional[int] = None
    rating: Optional[float] = None

class Rating(BaseModel):
    """Modèle pour une évaluation."""
    userId: int
    movieId: int
    rating: float = Field(..., ge=0.5, le=5.0)
    timestamp: Optional[int] = None

class Recommendation(BaseModel):
    """Modèle pour une recommandation."""
    movieId: int
    title: str
    genres: str
    score: float = Field(..., ge=0.0, le=1.0)
    reason: str

class UserProfile(BaseModel):
    """Modèle pour un profil utilisateur."""
    userId: int
    totalRatings: int
    averageRating: float
    favoriteGenres: List[str]
    lastActivity: datetime

class HealthResponse(BaseModel):
    """Modèle pour la réponse de santé."""
    status: str
    timestamp: datetime
    version: str
    uptime: float

# Initialisation de l'application FastAPI
app = FastAPI(
    title="🎬 CineRecommend API",
    description="API REST pour le système de recommandation de films intelligent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales
start_time = time.time()
movies_df = None
ratings_df = None

class DataManager:
    """Gestionnaire des données."""
    
    def __init__(self):
        self.project_root = project_root
        self.data_dir = self.project_root / "data"
        self.processed_dir = self.data_dir / "processed"
        self.load_data()
    
    def load_data(self):
        """Charge les données de films et d'évaluations."""
        global movies_df, ratings_df
        
        try:
            # Charger les données d'exemple
            movies_file = self.processed_dir / "movies_sample.csv"
            ratings_file = self.processed_dir / "ratings_sample.csv"
            
            if movies_file.exists() and ratings_file.exists():
                movies_df = pd.read_csv(movies_file)
                ratings_df = pd.read_csv(ratings_file)
                logger.info(f"Données chargées: {len(movies_df)} films, {len(ratings_df)} évaluations")
            else:
                # Créer des données d'exemple
                self.create_sample_data()
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données: {e}")
            self.create_sample_data()
    
    def create_sample_data(self):
        """Crée des données d'exemple."""
        global movies_df, ratings_df
        
        # Films d'exemple
        sample_movies = {
            'movieId': list(range(1, 101)),
            'title': [f'Film {i} ({1990 + i % 30})' for i in range(1, 101)],
            'genres': ['Action|Adventure', 'Comedy|Romance', 'Drama', 'Sci-Fi|Thriller', 'Horror'] * 20
        }
        
        # Évaluations d'exemple
        np.random.seed(42)
        sample_ratings = {
            'userId': np.random.randint(1, 51, 1000),
            'movieId': np.random.randint(1, 101, 1000),
            'rating': np.random.choice([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0], 1000),
            'timestamp': [int(time.time())] * 1000
        }
        
        movies_df = pd.DataFrame(sample_movies)
        ratings_df = pd.DataFrame(sample_ratings)
        
        logger.info("Données d'exemple créées")

# Initialiser le gestionnaire de données
data_manager = DataManager()

# Routes de l'API

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Route racine avec informations de l'API."""
    return {
        "message": "🎬 Bienvenue sur CineRecommend API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "movies": "/movies",
            "recommendations": "/recommend/user/{user_id}",
            "ratings": "/ratings",
            "search": "/movies/search"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérification de l'état de santé de l'API."""
    uptime = time.time() - start_time
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        uptime=uptime
    )

@app.get("/movies", response_model=List[Movie])
async def get_movies(
    limit: int = Query(20, ge=1, le=100, description="Nombre de films à retourner"),
    offset: int = Query(0, ge=0, description="Décalage pour la pagination")
):
    """Récupère la liste des films avec pagination."""
    if movies_df is None:
        raise HTTPException(status_code=500, detail="Données non disponibles")
    
    # Pagination
    start_idx = offset
    end_idx = offset + limit
    
    movies_subset = movies_df.iloc[start_idx:end_idx]
    
    movies = []
    for _, movie in movies_subset.iterrows():
        movies.append(Movie(
            movieId=int(movie['movieId']),
            title=movie['title'],
            genres=movie['genres']
        ))
    
    return movies

@app.get("/movies/{movie_id}", response_model=Movie)
async def get_movie(
    movie_id: int = Path(..., description="ID du film")
):
    """Récupère un film spécifique par son ID."""
    if movies_df is None:
        raise HTTPException(status_code=500, detail="Données non disponibles")
    
    movie_row = movies_df[movies_df['movieId'] == movie_id]
    
    if movie_row.empty:
        raise HTTPException(status_code=404, detail="Film non trouvé")
    
    movie = movie_row.iloc[0]
    
    # Calculer la note moyenne si disponible
    avg_rating = None
    if ratings_df is not None:
        movie_ratings = ratings_df[ratings_df['movieId'] == movie_id]
        if not movie_ratings.empty:
            avg_rating = float(movie_ratings['rating'].mean())
    
    return Movie(
        movieId=int(movie['movieId']),
        title=movie['title'],
        genres=movie['genres'],
        rating=avg_rating
    )

@app.get("/movies/search", response_model=List[Movie])
async def search_movies(
    query: str = Query(..., min_length=1, description="Terme de recherche"),
    limit: int = Query(10, ge=1, le=50, description="Nombre de résultats")
):
    """Recherche des films par titre."""
    if movies_df is None:
        raise HTTPException(status_code=500, detail="Données non disponibles")
    
    # Recherche insensible à la casse
    mask = movies_df['title'].str.contains(query, case=False, na=False)
    results = movies_df[mask].head(limit)
    
    movies = []
    for _, movie in results.iterrows():
        # Calculer la note moyenne
        avg_rating = None
        if ratings_df is not None:
            movie_ratings = ratings_df[ratings_df['movieId'] == movie['movieId']]
            if not movie_ratings.empty:
                avg_rating = float(movie_ratings['rating'].mean())
        
        movies.append(Movie(
            movieId=int(movie['movieId']),
            title=movie['title'],
            genres=movie['genres'],
            rating=avg_rating
        ))
    
    return movies

@app.get("/recommend/user/{user_id}", response_model=List[Recommendation])
async def get_user_recommendations(
    user_id: int = Path(..., description="ID de l'utilisateur"),
    n_recommendations: int = Query(10, ge=1, le=50, description="Nombre de recommandations")
):
    """Génère des recommandations pour un utilisateur."""
    if movies_df is None:
        raise HTTPException(status_code=500, detail="Données non disponibles")
    
    # Vérifier si l'utilisateur existe
    if ratings_df is not None:
        user_ratings = ratings_df[ratings_df['userId'] == user_id]
        if user_ratings.empty:
            # Nouvel utilisateur - recommandations populaires
            logger.info(f"Nouvel utilisateur {user_id} - recommandations populaires")
    
    # Simulation de recommandations (à remplacer par le vrai algorithme)
    np.random.seed(user_id)  # Pour des résultats reproductibles
    
    # Sélectionner des films aléatoires
    sample_movies = movies_df.sample(min(n_recommendations, len(movies_df)))
    
    recommendations = []
    for _, movie in sample_movies.iterrows():
        # Score simulé basé sur l'ID utilisateur et du film
        score = 0.5 + 0.4 * np.random.random()
        
        # Raison simulée
        reasons = [
            "Basé sur vos films préférés",
            "Populaire parmi les utilisateurs similaires",
            "Nouveau film tendance",
            "Correspond à vos genres favoris",
            "Recommandé par notre IA"
        ]
        
        recommendations.append(Recommendation(
            movieId=int(movie['movieId']),
            title=movie['title'],
            genres=movie['genres'],
            score=float(score),
            reason=np.random.choice(reasons)
        ))
    
    # Trier par score décroissant
    recommendations.sort(key=lambda x: x.score, reverse=True)
    
    return recommendations

@app.post("/ratings", response_model=Dict[str, Any])
async def add_rating(rating: Rating):
    """Ajoute une nouvelle évaluation."""
    global ratings_df
    
    if ratings_df is None:
        raise HTTPException(status_code=500, detail="Données non disponibles")
    
    # Vérifier si le film existe
    if movies_df is not None:
        movie_exists = movies_df['movieId'].isin([rating.movieId]).any()
        if not movie_exists:
            raise HTTPException(status_code=404, detail="Film non trouvé")
    
    # Ajouter l'évaluation
    new_rating = {
        'userId': rating.userId,
        'movieId': rating.movieId,
        'rating': rating.rating,
        'timestamp': rating.timestamp or int(time.time())
    }
    
    # Ajouter à DataFrame (en production, sauvegarder en base)
    new_row = pd.DataFrame([new_rating])
    ratings_df = pd.concat([ratings_df, new_row], ignore_index=True)
    
    logger.info(f"Nouvelle évaluation ajoutée: utilisateur {rating.userId}, film {rating.movieId}, note {rating.rating}")
    
    return {
        "message": "Évaluation ajoutée avec succès",
        "rating": new_rating
    }

@app.get("/users/{user_id}/profile", response_model=UserProfile)
async def get_user_profile(
    user_id: int = Path(..., description="ID de l'utilisateur")
):
    """Récupère le profil d'un utilisateur."""
    if ratings_df is None:
        raise HTTPException(status_code=500, detail="Données non disponibles")
    
    user_ratings = ratings_df[ratings_df['userId'] == user_id]
    
    if user_ratings.empty:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Calculer les statistiques
    total_ratings = len(user_ratings)
    avg_rating = float(user_ratings['rating'].mean())
    
    # Genres favoris (simulation)
    favorite_genres = ["Action", "Comedy", "Drama"]  # À calculer réellement
    
    # Dernière activité
    last_timestamp = user_ratings['timestamp'].max()
    last_activity = datetime.fromtimestamp(last_timestamp)
    
    return UserProfile(
        userId=user_id,
        totalRatings=total_ratings,
        averageRating=avg_rating,
        favoriteGenres=favorite_genres,
        lastActivity=last_activity
    )

@app.get("/stats", response_model=Dict[str, Any])
async def get_statistics():
    """Récupère les statistiques générales du système."""
    if movies_df is None or ratings_df is None:
        raise HTTPException(status_code=500, detail="Données non disponibles")
    
    # Calculer les statistiques
    total_movies = len(movies_df)
    total_ratings = len(ratings_df)
    total_users = ratings_df['userId'].nunique()
    avg_rating = float(ratings_df['rating'].mean())
    
    # Film le plus populaire
    movie_counts = ratings_df['movieId'].value_counts()
    most_popular_movie_id = movie_counts.index[0] if not movie_counts.empty else None
    most_popular_movie = None
    
    if most_popular_movie_id:
        movie_info = movies_df[movies_df['movieId'] == most_popular_movie_id]
        if not movie_info.empty:
            most_popular_movie = movie_info.iloc[0]['title']
    
    # Distribution des genres
    all_genres = []
    for genres_str in movies_df['genres'].dropna():
        genres = genres_str.split('|')
        all_genres.extend(genres)
    
    genre_counts = pd.Series(all_genres).value_counts().head(5).to_dict()
    
    return {
        "total_movies": total_movies,
        "total_ratings": total_ratings,
        "total_users": total_users,
        "average_rating": avg_rating,
        "most_popular_movie": most_popular_movie,
        "top_genres": genre_counts,
        "last_updated": datetime.now().isoformat()
    }

# Gestionnaire d'erreurs
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Gestionnaire d'erreurs HTTP personnalisé."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Gestionnaire d'erreurs général."""
    logger.error(f"Erreur non gérée: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erreur interne du serveur",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )

# Point d'entrée pour le développement
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )