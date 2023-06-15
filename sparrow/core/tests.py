from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import *


class IsTaggedTests(APITestCase):
    fixtures = ['testing-members.json', 'testing-attractions.json']

    def testConcurrentTagging(self):
        """
        Verify that any two users can concurrently change the tags of an attraction, as follows:
            - admin user tags attraction
            - regular user attempts to tag the same attraction with the same tag
            - regular user untags the attraction tagged by the admin
            - regular user tags attraction with another tag
            - admin user untags the attraction tagged by the regular user
            - admin user tags attraction with another tag
        """

        # get the url associated with the provided name
        listTagURL = reverse('core:isTagged-list')
        adminMember = User.objects.get(pk=1)
        regularMember = User.objects.get(pk=2)

        # creating first entry as the admin user
        self.client.force_login(adminMember)
        data = {'id': 1, 'tag': 1, 'attraction': 1}
        response = self.client.post(listTagURL, data)
        # make sure that the expected status code is returned 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # performing a list all, to verify that the data was modified as intended 
        response = self.client.get(listTagURL)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0], {'id': 1, 'tag': 1, 'attraction': 1})

        # attempting to create a duplicate (attraction, tag) entry as the regular user
        self.client.force_login(regularMember)
        data = {'id': 2, 'tag': 1, 'attraction': 1}
        response = self.client.post(listTagURL, data)
        # make sure that the expected status code is returned
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # deleting the entry inserted by the admin user, as the regular user
        detailTagURL = reverse('core:isTagged-detail', args=[1])
        response = self.client.delete(detailTagURL)
        # make sure that the expected status code is returned
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # performing a list all, to verify that the data was modified as intended
        response = self.client.get(listTagURL)
        self.assertEqual(len(response.data['results']), 0)

        # associating another tag to the same attraction, as the regular user
        data = {'id': 2, 'tag': 2, 'attraction': 1}
        response = self.client.post(listTagURL, data)
        # make sure that the expected status code is returned
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # performing a list all, to verify that the data was modified as intended
        response = self.client.get(listTagURL)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0], {'id': 2, 'tag': 2, 'attraction': 1})

        # deleting the entry inserted by the regular user, as the admin user
        self.client.force_login(adminMember)
        detailTagURL = reverse('core:isTagged-detail', args=[2])
        response = self.client.delete(detailTagURL)
        # make sure that the expected status code is returned
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # performing a list all, to verify that the data was modified as intended
        response = self.client.get(listTagURL)
        self.assertEqual(len(response.data['results']), 0)

        # finally, associating yet another tag to the same attraction, as the admin user
        data = {'id': 3, 'tag': 3, 'attraction': 1}
        response = self.client.post(listTagURL, data)
        # make sure that the expected status code is returned
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # performing a list all, to verify that the data was modified as intended
        response = self.client.get(listTagURL)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0], {'id': 3, 'tag': 3, 'attraction': 1})

