from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import City, UserSubscriptions, Subscription
from .permissions import MyPermissionIsAdminOrOwner
from .serializers import CitySerializer, SubscriptionSerializer


class CityListView(generics.ListAPIView):
    """
    A view that retrieves a list of cities.

    This view allows authenticated users to access a list of cities
    available in the system. The cities are retrieved from the City model
    and are serialized using the CitySerializer.
    """
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated]


class SubscriptionListView(generics.ListAPIView):
    """
    A view that retrieves a list of subscriptions for the authenticated user.

    This view allows authenticated users to access a list of their subscriptions.
    The subscriptions are retrieved based on the UserSubscriptions model, which
    stores a list of subscriptions associated with each user. The subscriptions
    are filtered based on the current user and are serialized using the
    SubscriptionSerializer.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve the subscriptions for the authenticated user.

        This method retrieves the subscriptions associated with the current
        authenticated user from the UserSubscriptions model. It then filters
        the Subscription objects based on the retrieved subscriptions and returns
        the filtered queryset.

        Returns:
            QuerySet: A queryset containing the subscriptions of the current user.
        """
        user_subscriptions = UserSubscriptions.objects.get(user=self.request.user)
        subscriptions = Subscription.objects.filter(id__in=user_subscriptions.subscriptions.all())
        return subscriptions

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests.

        This method checks if the current user has an entry in the UserSubscriptions
        model. If not, it creates an entry to store their subscriptions. Then, it
        proceeds with the default list handling by calling the parent class's
        `list` method to retrieve and return the user's subscription list.

        Returns:
            Response: The response containing the list of subscriptions of the
                      authenticated user.
        """
        if request.user not in [user.user for user in UserSubscriptions.objects.all()]:
            UserSubscriptions.objects.create(user=request.user)

        return self.list(request, *args, **kwargs)


class SubscriptionRetrieveView(generics.RetrieveUpdateDestroyAPIView):
    """
    A view that retrieves, updates, or deletes a specific subscription.

    This view allows authorized users to retrieve, update, or delete a specific
    subscription by providing its unique identifier (ID) in the URL. The view
    supports the HTTP methods GET, PUT, PATCH, and DELETE to perform these actions.
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [MyPermissionIsAdminOrOwner]

    def update(self, request, *args, **kwargs):
        """
        Update a specific subscription.

        This method updates the specified subscription with the provided data.
        The subscription is retrieved using its unique identifier (ID) from
        the URL, and the serializer is used to validate and save the updated data.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SubscriptionCreateView(generics.CreateAPIView):
    """
    A view that creates a new subscription for the authenticated user.

    This view allows authenticated users to create a new subscription by sending
    a POST request with the required subscription data. The user's authentication
    status is checked to ensure they have access to create subscriptions.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Create a new subscription for the authenticated user.

        This method creates a new subscription with the data provided in the request.
        The serializer is used to validate the data, and if valid, the subscription
        is saved. The created subscription is then associated with the authenticated user
        by adding it to the user's subscriptions in the UserSubscriptions model.

        Returns:
            Response: The response containing the details of the newly created subscription.
        """
        if not request.user.email:
            return Response('Wrong email address')

        serializer = SubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()

        user_subscriptions, _ = UserSubscriptions.objects.get_or_create(user_id=request.user.id)
        user_subscriptions.subscriptions.add(subscription)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
