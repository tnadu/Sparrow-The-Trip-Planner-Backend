from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import *


class MemberTests(APITestCase):
    fixtures = ['testing-members.json']

    def testProfilePhotoAndAccountRemoval(self):
        """
        Verify that the user making the request is able to remove their profile photo and then delete their account altogether
        """

        user = User.objects.get(pk=3)
        self.client.force_login(user)

        # verifying that the profile photo of the requested user is
        # different from the default one, according to the fixture
        memberDetailURL = reverse('core:member-detail', args=[3])
        response = self.client.get(memberDetailURL)
        self.assertNotEqual(response.data['profilePhoto'].split('/')[-1], 'default-profile-photo.jpeg')

        # removing the profile photo
        removeProfilePhotoURL = reverse('core:member-remove-profile-photo', args=[3])
        response = self.client.post(removeProfilePhotoURL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # and verifying the modification
        response = self.client.get(memberDetailURL)
        self.assertEqual(response.data['profilePhoto'].split('/')[-1], 'default-profile-photo.jpeg')

        # deleting the user account
        response = self.client.delete(memberDetailURL)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # and verifying the deletion
        try:
            deletedUser = User.objects.get(pk=3)
        except:
            deletedUser = None

        self.assertEqual(deletedUser, None)


class BelongsToTests(APITestCase):
    fixtures = ['testing-members.json', 'testing-groups.json', 'testing-belongsTo.json']

    def testCorrectListFiltering(self):
        """
        Verify that any given user is only able to view entries associated with a group that said user belongs to, as follows:
            - since the test-1 user does not belong to the group-2, the returned entries should not be associated with it
        """

        url = reverse('core:belongsTo-list')
        user = User.objects.get(pk=1)
        self.client.force_login(user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # the two users which belong to the same group and the user making the request
        self.assertEqual(len(response.data['results']), 3)
        self.assertNotIn({'user': 2, 'group': 2, 'isAdmin': True}, response.data['results'])


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
        adminUser = User.objects.get(pk=1)
        regularUser = User.objects.get(pk=2)

        # creating first entry as the admin user
        self.client.force_login(adminUser)
        data = {'id': 1, 'tag': 1, 'attraction': 1}
        response = self.client.post(listTagURL, data)
        # make sure that the expected status code is returned 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # performing a list all, to verify that the data was modified as intended 
        response = self.client.get(listTagURL)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0], {'id': 1, 'tag': 1, 'attraction': 1})

        # attempting to create a duplicate (attraction, tag) entry as the regular user
        self.client.force_login(regularUser)
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
        self.client.force_login(adminUser)
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

