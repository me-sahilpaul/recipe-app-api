
from rest_framework.test import APIClient
from rest_framework import status

from decimal import Decimal

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Recipe, Tag, Ingredients

from recipe.serializers import IngredientSerializer
 
INGREDIENTS_URL = reverse('recipe:ingredients-list')
RECIPE_URL =  reverse('recipe:recipe-list')

def create_user(email='sahil@example.com', password = 'testpass'):
    ''' Helper function for creating user'''
    return get_user_model().objects.create_user(email=email, password=password)

DEFAULT_RECIPE = {
        'title':'Sample Recipe Title',
        'time_minutes':22,
        'price':Decimal('5.75'),
        'description':'Sample Description',
        'link':'http://www.example.com/',
        'tags' : [{'name':'Dessert'}, {'name':'Dinner'}],
    }
def create_recipe(user, **params):
    """Helper function to create recipes"""
    DEFAULT_RECIPE.update(**params)

    return Recipe.objects.create(user = user, **params)

def detail_url(ingredient_id):
    """return Detail url of the recipe with ID provided"""
    return reverse('recipe:ingredients-detail',args=[ingredient_id])

class PublicIngredientsApiTests(TestCase):
    """ Test auth is required for retrieving ingredients."""

    def setUp(self):
        """ Setup menthod for the tests"""
        self.client = APIClient()
    
    def test_auth_required(self):
        """ Test auth is required for retrieving informaton"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.client.get(INGREDIENTS_URL)

class PrivateIngredientsApiTest(TestCase):
    """Test Authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user =  self.user)
    
    def test_retrieve_ingredients(self):
        """ Test retrieving a list of ingredients."""
        Ingredients.objects.create(user = self.user, name = "Kale")
        Ingredients.objects.create(user = self.user, name = "Vanilla")

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredients.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many = True )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user."""
        user2 = create_user(email =  'user2@example.com')
        Ingredients.objects.create(user = user2, name =  'Salt')
        ingredients = Ingredients.objects.create(user = self.user, name = 'Pepper')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredients.name)
        self.assertEqual(res.data[0]['id'], ingredients.id)
    
    def test_ingredients_update_fully(self):
        """Test update list of ingredients completely"""
        ingredients ={'ingredients' : [{'name':'salt'},{'name':'pepper'}] }
        payload = dict(DEFAULT_RECIPE)
        payload.update(ingredients)
        res = self.client.post(RECIPE_URL, payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        recipe_id = res.data['id']

        new_ingredients = {'ingredients' : [{'name':'sugar'},{'name':'flour'}]}
        payload.update(new_ingredients)
        
        url = detail_url(res.data['id'])
        res = self.client.put(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe_obj = Recipe.objects.filter(id=recipe_id,user=self.user).order_by('-id')
        recipe = recipe_obj[0]

        self.assertEqual(len(recipe.ingredients.all()),len(new_ingredients['ingredients']))
        for ingredients in new_ingredients['ingredients']:
            exists = recipe.ingredients.filter(
                name = ingredients['name'],
                user = self.user,
            ).exists()
            self.assertTrue(exists)
    
    def test_update_ingredients_partially(self):
        """Test to update the ingredients in recipe partially"""
        ingredients = {'ingredients': [{'name':'salt'},{'name':'pepper'}]}
        payload = dict(DEFAULT_RECIPE)
        payload.update(ingredients)

        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe_id = res.data['id']

        new_ingredient = {'ingredients': [{'name':'honey'}]}

        url =  detail_url(recipe_id)
        res = self.client.patch(url, new_ingredient, format = 'json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        recipe_obj = Recipe.objects.filter(id=recipe_id, user = self.user)
        recipe = recipe_obj[0]
        print(recipe.ingredients.all())
        self.assertEqual(len(recipe.ingredients.all()), 1)
        for each_ingredient in new_ingredient['ingredients']:
            exists = recipe.ingredients.filter(
                name = each_ingredient['name'],
                user = self.user,
            ).exists()
            self.assertTrue(exists)
    
    def test_delete_ingredient(self):
        """ Delete an Ingredient"""
        ingredient = Ingredients.objects.create(user = self.user, name = 'lettuce')
        url = detail_url(ingredient.id)
        print (url)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredients.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())




         

