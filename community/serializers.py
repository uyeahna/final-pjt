from rest_framework import serializers
from .models import Review, Comment
from accounts.models import User




class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['review', 'user', ]


# class ReviewListSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Review
#         fields = ('id', 'user', 'title', 'content', 'created_at', 'updated_at', 'rating',)
#         read_only_fields = ['user',]


class ReviewListSerializer(serializers.ModelSerializer):

    comment_count = serializers.IntegerField(source='comment_set.count', read_only=True)
    class Meta:
        model = Review
        fields = ('id', 'user', 'title', 'content', 'created_at', 'updated_at', 'comment_count', 'rating', 'movie')
        read_only_fields = ['user', 'movie']


class ReviewSerializer(serializers.ModelSerializer):
    # user = User(id=user_id)
    comment_set = CommentSerializer(read_only=True, many=True)
    
    class Meta:
        model = Review
        fields = ['id', 'title', 'content', 'comment_set', 'user', 'created_at', 'updated_at', 'rating', ]
        # fields = ['id', 'title', 'content', 'comment_set', 'comment_count', 'user', 'created_at', 'updated_at', 'rating', ]
        read_only_fields = ['user', ]

