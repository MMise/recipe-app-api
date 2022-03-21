from django.test import TestCase
from django.contrib.auth import get_user_model


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