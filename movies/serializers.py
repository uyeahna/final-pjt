from rest_framework import serializers
from .models import Movie, Rating, Genre
# from community.serializers import ReviewSerializer


class MovieSerializer(serializers.ModelSerializer):
    # review_set = ReviewSerializer(read_only=True, many=True)
    class Meta:
        model = Movie
        fields = '__all__'


class MovieListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Movie
        fields = '__all__'
        


class RatingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Rating
        # fields = ('rating',)
        fields = '__all__'
        read_only_fields = ['movie', 'user', ]


class GenreListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = '__all__'
        