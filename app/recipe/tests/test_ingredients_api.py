from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """Test the publicly available ingredients API."""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test the private ingredients API."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'testpassi',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Makkara')
        Ingredient.objects.create(user=self.user, name='Sinappi')

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients returned are for the user."""
        user2 = get_user_model().objects.create_user(
            'james.may@topgear.co.uk',
            'TeslaXR0ck5',
        )
        Ingredient.objects.create(user=user2, name='Makkara')
        ingredient = Ingredient.objects.create(user=self.user, name='Sinappi')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test that a new ingredient can be made."""
        payload = {'name': 'Kurkuma'}
        self.client.post(INGREDIENTS_URL, payload)

        self.assertTrue(
            Ingredient.objects.filter(user=self.user,
                                      name=payload['name']).exists()
        )

    def test_create_ingredient_invalid(self):
        """Test creating an ingredient with invalid name."""
        payload = {'name': ''}

        res = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipe(self):
        """Test filtering ingredients by those assigned to recipes."""
        ingredient1 = Ingredient.objects.create(
            user=self.user, name='Omena'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user, name='Suklaa'
        )
        recipe = Recipe.objects.create(
            title='Muru omena',
            time_minutes=15,
            price=3,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Test filtering ingredients by assigned return unique items."""
        ingredient1 = Ingredient.objects.create(user=self.user, name='Omena')
        Ingredient.objects.create(user=self.user, name='Suklaa')
        recipe = Recipe.objects.create(
            title='Muru omena',
            time_minutes=15,
            price=3,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)
        recipe2 = Recipe.objects.create(
            title='Nakit ja muussi',
            time_minutes=20,
            price=5,
            user=self.user
        )
        recipe2.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
