from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import *


class IsTaggedTests(APITestCase):
    fixtures = ['testing-members.json', 'testing-groups.json', 'testing-belongsTo.json', 'testing-attractions.json', 'testing-routes.json']

    def testConcurrentTagging(self):
        """
        Verify that any two users can concurrently change the tags of an attraction
        """

        # tagURL = reverse("isTagged-list")
