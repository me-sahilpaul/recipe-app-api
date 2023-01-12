"""Serializer for Recipe APIs"""

from rest_framework import serializers
from core.models import Recipe, Tag, Ingredients

class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients"""

    class Meta:
        model = Ingredients
        fields = ['id', 'name']
        read_only_fields = [ 'id' ]

class TagSerializer(serializers.ModelSerializer):
    """ Serializer for Tags Api"""

    class Meta:
        model = Tag
        fields = ['id','name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """ Serializer for recipe API."""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many = True, required=False)

    class Meta:
        model = Recipe
        fields = ['id','title','time_minutes','price','link','tags','ingredients']
        read_only_fields = ['id']
    
    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user = auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)
    
    def _get_or_create_ingredients(self, ingredients, recipe):
        """ Handle getting and creating Ingredients as need."""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, created = Ingredients.objects.get_or_create(
                user = auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """ Create a recipe."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        
        return recipe
    
    def update(self, recipe, validated_data):
        """ update recipe."""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        if tags is not None:
            recipe.tags.clear()
            self._get_or_create_tags(tags, recipe)
        
        if ingredients is not None:
            recipe.ingredients.clear()
            self._get_or_create_ingredients(ingredients, recipe)
        
        for attr, value in validated_data.items():
            setattr(recipe, attr, value)

        recipe.save()
        return recipe

class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail. """

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

