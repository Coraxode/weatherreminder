from django.conf.urls.static import static
from django.urls import include, path
from django.conf import settings
from . import views


urlpatterns = [
    path('api/cities/', views.CityListView.as_view(), name='cities'),
    path('api/my_subscriptions/', views.SubscriptionListView.as_view(), name='my_subscriptions'),
    path('api/my_subscriptions/<int:pk>/', views.SubscriptionRetrieveView.as_view(), name='subscription-detail'),
    path('api/subscribe/',  views.SubscriptionCreateView.as_view(), name='subscribe'),

    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
