from rest_framework.serializers import Serializer
from community import serializers
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.core.paginator import Paginator


from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .serializers import ReviewListSerializer, ReviewSerializer, CommentSerializer
from .models import Review, Comment
from movies.models import Movie


@api_view(['GET', 'POST'])
@authentication_classes([JSONWebTokenAuthentication])
@permission_classes([IsAuthenticated])
def review_list_create(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    
    if request.method == 'GET':
        myReview = request.GET.get('myReview')
        next = request.GET.get('next')
        page = request.GET.get('page')
        # print(myReview, '5' * 200)
        if myReview == 'true':
            # review = movie.review_set.filter(user_id=request.user)
            review = get_object_or_404(movie.review_set, user_id=request.user)
            print(review)
            serializer = ReviewListSerializer(review)
            return Response(serializer.data)
        elif next == 'true':
            reviews = movie.review_set.all()
            paginator = Paginator(reviews, 15)
            current_page = paginator.page(page)
            return JsonResponse({'next': current_page.has_next()})
        else:
            reviews = movie.review_set.all()
            paginator = Paginator(reviews, 15)
            page_obj = paginator.get_page(page)
            serializer = ReviewListSerializer(page_obj, many=True)
            return Response(serializer.data)

    elif request.method == 'POST':
        review = Review.objects.filter(movie_id=movie.id, user_id=request.user)
        if review.count() == 0:
        #     review.delete()
            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(movie=movie, user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@authentication_classes([JSONWebTokenAuthentication])
@permission_classes([IsAuthenticated])
def review_detail_update_delete_comment_create(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.method == 'GET':
        serializer = ReviewSerializer(review)
        return Response(serializer.data)


    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(review=review, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


    if request.user == review.user:
        if request.method == 'PUT':
            # print(request.user, review.user)
            serializer = ReviewSerializer(review, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)


        elif request.method == 'DELETE':
            if request.user == review.user:
                review.delete()
                return Response({ 'id': review_pk })
    return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['PUT', 'DELETE'])
@authentication_classes([JSONWebTokenAuthentication])
@permission_classes([IsAuthenticated])
def comment_update_delete(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    
    if request.user == comment.user:
        if request.method == 'PUT':
            serializer = CommentSerializer(comment, request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)

        elif request.method == 'DELETE':
            comment.delete()
            return Response({ 'id': comment_pk })
    return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET',])
@authentication_classes([JSONWebTokenAuthentication])
@permission_classes([IsAuthenticated])
def comment_list(request, review_pk):
    next = request.GET.get('next')
    page = request.GET.get('page')
    comments = get_list_or_404(Comment, review_id=review_pk)
    paginator = Paginator(comments, 20)
    page_obj = paginator.get_page(page)
    serializer = CommentSerializer(page_obj, many=True)

    if next == 'true':
        current_page = paginator.page(page)
        return JsonResponse({
            'next': current_page.has_next() 
        })

    return Response(serializer.data)