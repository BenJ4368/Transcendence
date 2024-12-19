from django.urls import path, include
from a_users.views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', profile_view, name="profile"),
    path('edit/', profile_edit_view, name="profile-edit"),
    path('onboarding/', profile_edit_view, name="profile-onboarding"),
    path('settings/', profile_settings_view, name="profile-settings"),
    path('emailchange/', profile_emailchange, name="profile-emailchange"),
    path('emailverify/', profile_emailverify, name="profile-emailverify"),
    path('delete/', profile_delete_view, name="profile-delete"),

    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('jwt_exchange/', jwt_exchange, name='jwt_exchange'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='user_logout'),

    path('disable_2fa/', disable_2fa, name='disable_2fa'),
    path('setup_2fa/', setup_2fa, name='setup_2fa'),
    path('backup_tokens/', backup_tokens, name='backup_tokens'),
    path('login/', login_2fa, name='login'),

    path('friends/<str:section>/', friends, name='friends'),
    path('friends/sending/<str:username>', create_friend_request, name='send_friend_request'),
    path('friends/accept/<str:username>', accept_friend_request, name='accept_request'),
    path('friends/reject/<str:username>', reject_friend_request, name='reject_request'),
    path('friends/delete/<str:username>', delete_friend, name='delete_friend'),
]