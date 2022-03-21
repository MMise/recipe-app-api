from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email="test@test.fi", password="nakki"):
    """Create a test user."""
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):

    def test_create_user_with_email_successfull(self):
        """Test creating a new user with an email."""
        email = "test@keknet.com"
        password = "nakki"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test that the email for a new user is normalized."""
        email = "test@KEKNET.COM"
        user = get_user_model().objects.create_user(
            email=email,
            password="nakki"
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test that an invalid email raises an error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email="", password="")

    def test_create_new_superuser(self):
        """Test that a new superuser can be created."""
        user = get_user_model().objects.create_superuser(
            email="test@keknet.com",
            password="nakki"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation."""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan',
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation."""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Pepino',
        )

        self.assertEqual(str(ingredient), ingredient.name)
