from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from a_users.views import profile_view
from a_home.views import *

from two_factor.urls import urlpatterns as tf_urls

urlpatterns = [
    path('admin/', admin.site.urls),
	path('accounts/', include('allauth.urls')),
	path('', include('a_home.urls')),
    path('', include(tf_urls)),
	path('profile/', include('a_users.urls')),
	path('@<username>/', profile_view, name="profile")
]

#only used in developpement
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)