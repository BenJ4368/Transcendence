from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from two_factor.urls import urlpatterns as tf_urls

from app_transcendence.views import register, home, jwt_exchange, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', include(tf_urls)),

    path('jwt_exchange/', jwt_exchange, name='jwt'),

    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),

    path('home/', home, name='home'),
]
