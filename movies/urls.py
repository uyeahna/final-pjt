from django.urls import path
from . import views


urlpatterns = [
    path('getmovies/', views.getmovies),
    # path('gethome/', views.gethome),
    path('', views.home),
    path('recommendation/', views.recommendation),
    path('recommendation_genre/', views.recommendation_genre),
    path('<int:movie_pk>/', views.movie_detail_rating_create),
    path('<int:movie_pk>/rating/', views.rating_read),
]