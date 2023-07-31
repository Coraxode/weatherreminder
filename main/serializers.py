from rest_framework import serializers
from main.models import City, Subscription


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    city_name = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = '__all__'

    @staticmethod
    def get_city_name(obj):
        return str(obj.city)
