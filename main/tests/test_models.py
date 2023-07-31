from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.test import TestCase
from django.contrib.auth.models import User
from ..models import City, Subscription, UserSubscriptions


class CityModelTest(TestCase):
    def test_city_name_display(self):
        city_name = "New York"
        city = City.objects.create(name=city_name)
        self.assertEqual(str(city), city_name)

    def test_city_current_weather(self):
        city_name = "Los Angeles"
        current_weather_info = "Sunny"
        city = City.objects.create(name=city_name, current_weather=current_weather_info)
        self.assertEqual(city.current_weather, current_weather_info)

    def test_city_without_current_weather(self):
        city_name = "Paris"
        city = City.objects.create(name=city_name)
        self.assertEqual(city.current_weather, "")

    def test_city_name_max_length(self):
        city_name = "A" * 51
        with self.assertRaises(Exception):
            City.objects.create(name=city_name).full_clean()

    def test_update_city_weather(self):
        city_name = "London"
        initial_weather_info = "Cloudy"
        updated_weather_info = "Rainy"
        city = City.objects.create(name=city_name, current_weather=initial_weather_info)

        city.current_weather = updated_weather_info
        city.save()

        updated_city = City.objects.get(pk=city.pk)
        self.assertEqual(updated_city.current_weather, updated_weather_info)

    def test_delete_city(self):
        city_name = "Tokyo"
        city = City.objects.create(name=city_name)

        city.delete()

        with self.assertRaises(City.DoesNotExist):
            City.objects.get(name=city_name)


class SubscriptionModelTest(TestCase):
    def setUp(self):
        self.city = City.objects.create(name='Test City')
        self.valid_notification_period = 3
        self.invalid_notification_period = 0.5

    def test_subscription_creation(self):
        subscription = Subscription.objects.create(city=self.city, notification_period=self.valid_notification_period)
        self.assertEqual(str(subscription), f"Test City, notification period: {self.valid_notification_period} hours.")

    def test_invalid_notification_period(self):
        with self.assertRaises(ValidationError):
            Subscription.objects.create(city=self.city, notification_period=self.invalid_notification_period).full_clean()

    def test_notification_period_min_value_validator(self):
        subscription = Subscription(city=self.city, notification_period=0.75)
        min_value_validator = [v for v in subscription._meta.get_field('notification_period').validators if isinstance(v, MinValueValidator)]
        self.assertEqual(len(min_value_validator), 1)

        with self.assertRaises(ValidationError):
            subscription.full_clean()


class UserSubscriptionsModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.city = City.objects.create(name='Test City')
        self.subscription = Subscription.objects.create(city=self.city, notification_period=5)

    def test_user_subscriptions_creation(self):
        user_subscriptions = UserSubscriptions.objects.create(user=self.user)
        self.assertEqual(str(user_subscriptions), f"{self.user}'s subscriptions")

    def test_user_subscriptions_with_subscription(self):
        user_subscriptions = UserSubscriptions.objects.create(user=self.user)
        user_subscriptions.subscriptions.add(self.subscription)

        self.assertTrue(self.subscription in user_subscriptions.subscriptions.all())

    def test_user_subscriptions_without_subscription(self):
        user_subscriptions = UserSubscriptions.objects.create(user=self.user)
        self.assertFalse(user_subscriptions.subscriptions.exists())

    def test_user_subscriptions_many_to_many_relationship(self):
        user_subscriptions = UserSubscriptions.objects.create(user=self.user)
        user_subscriptions.subscriptions.add(self.subscription)

        self.assertTrue(self.subscription.usersubscriptions_set.exists())
        self.assertEqual(self.subscription.usersubscriptions_set.first(), user_subscriptions)

        self.assertTrue(self.user.usersubscriptions_set.exists())
        self.assertEqual(self.user.usersubscriptions_set.first(), user_subscriptions)
