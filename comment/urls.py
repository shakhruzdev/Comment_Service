from django.urls import path
from .views import CommentViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('login/', TokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('comment/', CommentViewSet.as_view({'post': 'create'})),
    path('comments/', CommentViewSet.as_view({'get': 'get_all'})),
    # path('comment/<int:pk>/', CommentViewSet.as_view({'patch': 'update'})),
    path('commente/<int:pk>/', CommentViewSet.as_view({'get': 'get_by_id'})),
    path('commenta/<int:pk>/', CommentViewSet.as_view({'delete': 'destroy'})),
]
