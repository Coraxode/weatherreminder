from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import City, UserSubscriptions, Subscription
from .permissions import MyPermissionIsAdminOrOwner
from .serializers import CitySerializer, SubscriptionSerializer


class CityListView(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated]


class SubscriptionListView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_subscriptions = UserSubscriptions.objects.get(user=self.request.user)
        subscriptions = Subscription.objects.filter(id__in=user_subscriptions.subscriptions.all())
        return subscriptions

    def get(self, request, *args, **kwargs):
        if request.user not in [user.user for user in UserSubscriptions.objects.all()]:
            UserSubscriptions.objects.create(user=request.user)

        return self.list(request, *args, **kwargs)


class SubscriptionRetrieveView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [MyPermissionIsAdminOrOwner]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SubscriptionCreateView(generics.CreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not request.user.email:
            return Response('Wrong email address')

        serializer = SubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()

        user_subscriptions, _ = UserSubscriptions.objects.get_or_create(user_id=request.user.id)
        user_subscriptions.subscriptions.add(subscription)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
