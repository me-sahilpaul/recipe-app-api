"""
Tests for Models
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

def create_user(email="user@example.com",password="Pass123"):
    """Helper function to create and return a user"""
    return get_user_model().objects.create_user(
        email = email,
        password = password,
    )

class ModelTest(TestCase):
    """Test Models"""

    def test_create_user_with_email_successful(self):
        """ Test creating a user with an email is successful."""
        email = "sahil@example.com"
        password = "sahil1231"
        user = get_user_model().objects.create_user(
            email = email,
            password = password,
        )

        self.assertEquals(user.email,email)
        self.assertTrue(user.check_password(password))

    def test_new_user_normalized(self):
        """Test Email is normalized for new users"""
        sample_emails=[
            ["test1@EXAMPLE.com","test1@example.com"],
            ["Test2@Example.com","Test2@example.com"],
            ['TEST3@EXAMPLE.COM',"TEST3@example.com"],
            ['test4@example.COM',"test4@example.com"],

        ]
        
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email,'sample123')
            self.assertEquals(user.email, expected)

    def test_new_user_without_email_raise_error(self):
        """Test that creating a user without email will raise an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("","test123")
    
    def test_create_superuser(self):
        """test create a superuser."""
        user = get_user_model().objects.create_superuser(
            'superuser@example.com',
            '1234'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
    
    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )

        recipe = models.Recipe.objects.create(
            user = user,
            title = "Sample Recipe name",
            time_minutes = 5,
            price = Decimal('5.50'),
            description = "Sample discription.",
        )

        self.assertEqual(str(recipe), recipe.title )
    
    def test_create_tag(self):
        """ Test creating a tag is successfull"""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name="Tag1")

        self.assertEqual(str(tag),tag.name)