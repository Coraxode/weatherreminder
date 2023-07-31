from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from main.models import City, Subscription, UserSubscriptions
from main.serializers import SubscriptionSerializer


class CityListViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.city1 = City.objects.create(name='Tokyo', current_weather='Sunny')
        self.city2 = City.objects.create(name='London', current_weather='Rainy')
        self.url = reverse('cities')

    def test_city_list_view_authenticated(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        self.assertEqual(response.data[0]['name'], self.city1.name)
        self.assertEqual(response.data[0]['current_weather'], self.city1.current_weather)
        self.assertEqual(response.data[1]['name'], self.city2.name)
        self.assertEqual(response.data[1]['current_weather'], self.city2.current_weather)

    def test_city_list_view_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SubscriptionListViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        self.city1 = City.objects.create(name='Tokyo', current_weather='Sunny')
        self.city2 = City.objects.create(name='Albuquerque', current_weather='Rainy')
        self.subscription1 = Subscription.objects.create(city=self.city1, notification_period=3)
        self.subscription2 = Subscription.objects.create(city=self.city2, notification_period=5)

        self.url = reverse('my_subscriptions')

    def test_user_subscriptions_created(self):
        UserSubscriptions.objects.all().delete()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(UserSubscriptions.objects.filter(user=self.user).exists())

    def test_user_subscriptions_list_authenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subscriptions = Subscription.objects.filter(id__in=UserSubscriptions.objects.get(user=self.user).subscriptions.all())
        self.assertEqual(len(response.data), subscriptions.count())

        serializer = SubscriptionSerializer(subscriptions, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_user_subscriptions_list_unauthenticated(self):
        self.client.logout()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SubscriptionRetrieveViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.user_subscriptions = UserSubscriptions.objects.create(user=self.user)

        self.city = City.objects.create(name='City1', current_weather='Sunny')
        self.subscription = Subscription.objects.create(city=self.city, notification_period=3)

        self.user_subscriptions.subscriptions.add(self.subscription)
        self.url = reverse('subscription-detail', args=[self.subscription.id])

    def test_subscription_retrieve_authenticated_owner(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = SubscriptionSerializer(self.subscription)
        self.assertEqual(response.data, serializer.data)

    def test_subscription_retrieve_authenticated_admin(self):
        self.user.is_staff = True
        self.user.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = SubscriptionSerializer(self.subscription)
        self.assertEqual(response.data, serializer.data)

    def test_subscription_update_authenticated_owner(self):
        updated_notification_period = 5
        data = {'notification_period': updated_notification_period}
        response = self.client.put(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_subscription = Subscription.objects.get(id=self.subscription.id)
        self.assertEqual(updated_subscription.notification_period, updated_notification_period)

    def test_subscription_delete_authenticated_owner(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subscription.objects.filter(id=self.subscription.id).exists())
