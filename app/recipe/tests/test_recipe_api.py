""" Tests for Recipe API """

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def create_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults={
        'title':'Sample Recipe Title',
        'time_minutes':22,
        'price':Decimal('5.75'),
        'description':'Sample Description',
        'link':'http://www.example.com/',
    }

    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

class PublicRecipeAPITests(TestCase):
    """ Test unauthorized API requests"""

    def setUp(self):
        self.client=APIClient()
    
    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@example.com",
            "pass123",
        )
        self.client.force_authenticate(self.user)
    
    def test_retrive_recipes(self):
        """Test retriving a list of recipes."""
        create_recipe( user = self.user)
        create_recipe( user = self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_recipe_limited_to_user(self):
        """Test retriving a list of recipes."""
        other_user = get_user_model().objects.create_user(
            'otherUser@example.com',
            'test_pass',
        )
        create_recipe( user = other_user)
        create_recipe( user = self.user)
        
        res = self.client.get(RECIPES_URL)

        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)