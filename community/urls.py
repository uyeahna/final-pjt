from django.urls import path
from . import views

urlpatterns = [
    path('<int:movie_pk>/', views.review_list_create),
    path('review/<int:review_pk>/', views.review_detail_update_delete_comment_create),
    path('review/<int:review_pk>/comment/', views.comment_list),
    path('comment/<int:comment_pk>/', views.comment_update_delete),
]