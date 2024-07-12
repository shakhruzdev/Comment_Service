from django.urls import path
from .views import CommentViewSet

urlpatterns = [
    path('comment/', CommentViewSet.as_view({'post': 'create'})),
    path('comments/', CommentViewSet.as_view({'get': 'get_all'})),
    path('comment/<float:pk>/', CommentViewSet.as_view({'get': 'get_by_id', 'delete': 'destroy'})),
    path('post/', CommentViewSet.as_view({'get': 'post_comments'})),
]
