"""Views for the Recipe API's"""

from rest_framework import (
    viewsets, 
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
        Recipe, 
        Tag, 
        Ingredients,
)

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

class BaseRecipeAttrsViewSet(mixins.ListModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.UpdateModelMixin,
                                viewsets.GenericViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve Tags for an authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

class TagViewSet(BaseRecipeAttrsViewSet):
    """Manage Tags in the database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()

    

class IngredientViewSet(BaseRecipeAttrsViewSet):
    """Manage Ingredients in the database"""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredients.objects.all()