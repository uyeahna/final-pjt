from django.contrib import admin
from .models import Movie, Rating, Movie_genre

# Register your models here.

admin.site.register(Movie)
admin.site.register(Movie_genre)
admin.site.register(Rating)
