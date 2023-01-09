"""Views for the Recipe API's"""

from rest_framework import (
    viewsets, 
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag
from recipe import serializers

class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage  recipe API."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == "list":
            return serializers.RecipeSerializer
        
        return self.serializer_class
    
    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

class TagsViewSets(mixins.UpdateModelMixin, 
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet,
                    mixins.DestroyModelMixin):
    """Manage Tags in the database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all().order_by('-id')
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve Tags for an authenticated user"""
        return Tag.objects.filter(user=self.request.user).order_by('-id')
