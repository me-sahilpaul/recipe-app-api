""" Tests for Recipe API """

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Create and return a recipe detail."""
    return reverse('recipe:recipe-detail',args=[recipe_id])

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

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)

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
        self.user=create_user( email="test@example.com", password="pass123")
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
        other_user = create_user( email='otherUser@example.com',password='test_pass')
        create_recipe( user = other_user)
        create_recipe( user = self.user)
        
        res = self.client.get(RECIPES_URL)

        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_egt_recipe_default(self):
        """Test get recipe details"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serialzer = RecipeDetailSerializer (recipe)
        self.assertEqual(res.data, serialzer.data)

    def test_create_recipe(self):
        """Test creating a recipe"""
        payload={
        'title':'Sample Recipe',
        'time_minutes':22,
        'price':Decimal('5.75'),
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self. assertEqual(getattr(recipe, key),value)
        
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update of a recipe"""
        original_link = "http://example.com/recipe.pdf"
        recipe = create_recipe (
            user = self.user,
            title = 'Sample recipe tilte',
            link = original_link
        )

        payload = {'title':'New updated Title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        orignal={
        'title':'Sample Recipe Title',
        'time_minutes':22,
        'price':Decimal('5.75'),
        'description':'Sample Description',
        'link':'http://www.example.com/',
        }
        recipe = create_recipe(
            user = self.user,
            **orignal
        )
        modified = {'title':'Sample Recipe Modified',
        'time_minutes':10,
        'price':Decimal('6'),
        'description':'Sample Modified',
        'link':'http://www.example.com/modified',
        }
        url = detail_url(recipe_id=recipe.id)
        res = self.client.put(url, modified)
        self.assertEqual(recipe.user, self.user)
        recipe.refresh_from_db()
        for key, value in modified.items():
            self.assertEqual(getattr(recipe, key),value)

        self.assertEqual(res.status_code,status.HTTP_200_OK)

    def test_update_user_returns_error(self):
        """Updating user generates error"""
        new_user = create_user(email="u2@example.com",password="sahil1231")
        recipe = create_recipe(user=self.user)

        payload = {'user':new_user.id}
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)
    
    def test_delete_recipe(self):
        """Test deleting recipe successful."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """user trying to delete someone else recipe"""
        new_user = create_user(email="nwu@example.com", password="newpassword")
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
        