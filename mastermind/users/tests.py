from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class UserAPITest(APITestCase):

    def test_create_existing_user(self):
        """Test creating a user with the same username as a previously existing one"""
        User.objects.create_user('testuser', password='testpassword')
        url = reverse('create-user')

        json = {
            'username': 'testuser',
            'password': 'doesntmatter'
        }

        response = self.client.post(url, json, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, 'This user already exists')

    def test_create_wrong_users(self):
        """Test creating users with incorrect usernames or passwords"""
        url = reverse('create-user')

        json = {
            'username': '',
            'password': 'doesntmatter'
        }

        response = self.client.post(url, json, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field may not be blank.', response.data['username'])

        json = {
            'username': 'testuser',
            'password': ''
        }

        response = self.client.post(url, json, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field may not be blank.', response.data['password'])

        json = {
            'username': 'ûẗëẅỳù',
            'password': 'doesntmatter'
        }

        response = self.client.post(url, json, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Enter a valid username.', response.data['username'][0])

        json = {
            'username': 'testuser',
            'password': 'jfdklss'
        }

        response = self.client.post(url, json, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This password is too short.', response.data['password'][0])

        json = {
            'username': 'testuser',
            'password': 'abcd1234'
        }

        response = self.client.post(url, json, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This password is too common.', response.data['password'][0])

        json = {
            'username': 'testuser',
            'password': '65465165165'
        }

        response = self.client.post(url, json, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This password is entirely numeric.', response.data['password'][0])

    def test_create_new_user(self):
        """Test correctly creating a new user"""
        url = reverse('create-user')
        json = {
            'username': 'testuser',
            'password': 'testpassword'
        }

        response = self.client.post(url, json, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Token.objects.count(), 1)
        self.assertEqual(Token.objects.get().key, response.data['token'])
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get(), Token.objects.get().user)
