from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient

from .models import Tweet
import random, string

User = get_user_model()

class TweetTestCase(TestCase):
    def setUp(self):
        self.users = {}
        for i in range(1, 10):
            name = ''
            for index in range(1, 10):
                name += random.choice(string.ascii_lowercase)
            self.users[name] = User.objects.create(username=name, password='createnewpassword')


    def test_tweet_created(self):
        def get_client(user):
            client = APIClient()
            client.login(username=user.username, password='createnewpassword')
            return client

        tweet_count = 0
        for username, user in self.users.items():
            created_tweet = Tweet.objects.create(content="My New Tweet", user=user)
            tweet_count += 1
            self.assertEqual(created_tweet.user, user)
            # Test getting tweet list view from REST
            client = get_client(user=user)
            response = client.get('/api/tweets/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), tweet_count)
            print(response)
