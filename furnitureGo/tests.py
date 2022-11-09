from django.test import TestCase
from .models import User

# Create your tests here.
class TestModel(TestCase):
    def test_should_create_user(self):
        user = User.objects.create_user(username ='username', email ='username@gmail.com')
        user.set_password('password123')
        user.save()
        self.assertEqual(str(user), 'username')