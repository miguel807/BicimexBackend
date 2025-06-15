from django.urls import path, include
from rest_framework import routers
from .api import CommentViewSet, FeedbackViewSet

router = routers.DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comments') 
router.register(r'feedbacks', FeedbackViewSet)

urlpatterns = [
    path('', include(router.urls)),
]