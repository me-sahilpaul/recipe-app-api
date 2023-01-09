"""
Tests for the tags API.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from core.models import Tag

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import TagSerializer


TAGS_URL = reverse("recipe:tag-list")

def detail_url(tag_id):
    """Detail of tag ID"""
    return reverse("recipe:tag-detail", args=[tag_id])


def create_user(email="sample@example.com", password="sahil123"):
    """Create user helper Function"""
    return get_user_model().objects.create_user(email, password)

class PublicTagAPITests(TestCase):
    """ Test unauthenticated API Requests."""

    def setUp(self):
        self.client=APIClient()

    def test_auth_required(self):
        """Test Authentication is required to access tags"""

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    

class PrivateTagAPITests(TestCase):
    """ Test for authenticated users. """
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_tags(self):
        """Test retriving a list of tags"""
        
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")
        

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('name')
        serialzer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialzer.data)
    
    def test_tags_limited_to_user(self):
        """Test List of tags is limited to authenticated users"""
        user_new = create_user("user2@example.com")
        tag =Tag.objects.create(user=self.user, name="Vegan")
        tag2= Tag.objects.create(user=user_new, name="Vegiterian")
        

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)
    
    def test_update_tag(self):
        """Test Update a Tag."""
        tag = Tag.objects.create(user=self.user, name = "TAG1")

        payload = { 'name':"Google" }

        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        
        self.assertEqual(tag.name, payload['name'])
    
    def test_delete_tag(self):
        """Test if tag could be deleted"""

        tag = Tag.objects.create(user=self.user, name = "NEW TAG")

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())
        

        
        
