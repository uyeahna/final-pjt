import re
from django.db.models.deletion import RestrictedError
from rest_framework import serializers
from rest_framework.serializers import Serializer
from django.shortcuts import get_object_or_404, get_list_or_404
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
import heapq


from .serializers import GenreListSerializer, MovieListSerializer, MovieSerializer, RatingSerializer
from .models import Genre, Movie, Movie_genre, Rating

import requests, json
import urllib.request
from django.db.models import Q


@api_view(['GET',])
def home(request):
    # movies = get_list_or_404(Movie)
    movies = Movie.objects.all().order_by('-vote_count')
    paginator = Paginator(movies, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    serializer = MovieListSerializer(page_obj, many=True)

    # for movie in movies:
    #     genres = Movie_genre.objects.filter(movie_id=movie.id)
    #     # print(genres)
    #     for genre in genres:
    #         # print(genre.genre_id)

    #         genre_kr = Genre.objects.filter(id=genre.genre_id)
    #         print(genre_kr.name)

    return Response(serializer.data)





@api_view(['GET', 'POST',])
@authentication_classes([JSONWebTokenAuthentication])
@permission_classes([IsAuthenticated])
def movie_detail_rating_create(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.method == 'GET':
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    elif request.method == 'POST':
        print(request.data)
        rating = Rating.objects.filter(movie_id=movie.id, user_id=request.user)
        print(rating.count())
        if request.data['rating'] != '0':
            if rating.count() >= 1:
                rating.delete()

            serializer = RatingSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(movie=movie, user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
        elif request.data['rating'] == '0':
            rating.delete()
            return Response(status=status.HTTP_200_OK)


@api_view(['GET',])
@authentication_classes([JSONWebTokenAuthentication])
@permission_classes([IsAuthenticated])
def rating_read(request, movie_pk):
    # rating = Rating.objects.filter(movie_id=movie_pk, user_id=request.user)
    rating = get_object_or_404(Rating, movie_id=movie_pk, user_id=request.user)
    serializer = RatingSerializer(rating)
    return Response(serializer.data)
    


url = 'https://api.themoviedb.org/3/trending/movie/week?api_key=b90a017ddefee0bcc540fa67b1b9f2a0&language=ko-KR'


@api_view(['GET',])
def getmovies(request):
    popular_url = 'https://api.themoviedb.org/3/movie/popular?api_key=b90a017ddefee0bcc540fa67b1b9f2a0&language=ko-KR&page='
    for z in range(1, 26):
    # url = 'https://api.themoviedb.org/3/trending/movie/week?api_key=b90a017ddefee0bcc540fa67b1b9f2a0&language=ko-KR'
        
        url = popular_url + str(z)
        # 나는 json
        res = requests.get(url).json()
        for movie_data in res['results']:
            movie = Movie()
            
            movie.id = movie_data['id']
            movie.title = movie_data['title']
            if movie_data.get('release_date') == None or movie_data.get('release_date') == "":
                pass
            else:
                movie.release_date = movie_data['release_date']
            if movie_data.get('popularity') == None or movie_data.get('popularity') == "":
                movie.popularity = 0
            else:
                movie.popularity = movie_data['popularity']
            
            movie.vote_count = movie_data['vote_count']
            movie.vote_average = movie_data['vote_average']
            movie.overview = movie_data['overview']
            movie.poster_path = movie_data['poster_path']
            movie.save()

            for genre_id in movie_data['genre_ids']:
                genre = Movie_genre()
                genre.movie_id = movie.id
                genre.genre_id = genre_id
                genre.save()

    return Response(status=status.HTTP_200_OK)


@api_view(['GET',])
@authentication_classes([JSONWebTokenAuthentication])
@permission_classes([IsAuthenticated])
def recommendation(request):
    user = request.user
    genre_id = request.GET.get('genre_id')
    movies_watched = user.rating_set.all()
    movies_watched_ids = []

    for movie in movies_watched:
        movies_watched_ids.append(movie.movie_id)

    if int(genre_id) in [12, 14, 16, 18, 27, 28, 35, 36, 37, 53, 80, 99, 878, 9648, 10402, 10749, 10751, 10752, 10770]:
        movie_ids = Movie_genre.objects.filter(genre_id=genre_id).exclude(movie_id__in=movies_watched_ids)

    recommendation_list = []
    for movie_id in movie_ids:
        recommendation_list.append(movie_id.movie_id)
    movies = Movie.objects.order_by('-vote_count').filter(id__in=recommendation_list)[:5]
    serializer = MovieListSerializer(movies, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET',])
@authentication_classes([JSONWebTokenAuthentication])
@permission_classes([IsAuthenticated])
def recommendation_genre(request):
    user = request.user
    print(user)
    movies_watched = user.rating_set.all()
    genre_dict = {n:0 for n in [12, 14, 16, 18, 27, 28, 35, 36, 37, 53, 80, 99, 878, 9648, 10402, 10749, 10751, 10752, 10770]}
    for rating in movies_watched:
        # 별점이 3점 이상이면
        if rating.rating >= 3:
            genres = Movie_genre.objects.all().filter(movie_id=rating.movie_id)
            for genre in genres:
                genre_dict[genre.genre_id] += 1
    
    arr = [12, 14, 16, 18, 27, 28, 35, 36, 37, 53, 80, 99, 878, 9648, 10402, 10749, 10751, 10752, 10770]
    cnt = [] # 최대힙으로 해당 유저의 장르가 저장됨.
    recommend_genre = []
    # 네번뽑으면 된다.
    for key, val in genre_dict.items():
        heapq.heappush(cnt, (-val, key))

    for n in range(4):
        v, key = heapq.heappop(cnt)
        if v != 0:
            recommend_genre.append(key)

    recommend_genre_kr = Genre.objects.filter(id__in=recommend_genre)
    serializer = GenreListSerializer(recommend_genre_kr, many=True)


    return Response(serializer.data, status=status.HTTP_200_OK)
