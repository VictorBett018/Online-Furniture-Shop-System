from django.test import TestCase

from furnitureGo.models import User
from .models import *
# Create your tests here.
class CreateUserTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
        full_name = "Vic Bett",
        address = "nairobi",
        )
    def test_product_created(self):
        self.assertEquals(self.user1.full_name, "Vic Bett")