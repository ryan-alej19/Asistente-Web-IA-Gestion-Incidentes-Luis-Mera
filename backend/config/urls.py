from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from users.views import CustomAuthToken
from django.http import HttpResponse
from incidents.views import health_check
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve

def root_view(request):
    return HttpResponse("Backend incident system running. Go to /admin or /api/...", status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/', CustomAuthToken.as_view()),
    path('api/incidents/', include('incidents.urls')),
    path('api/health/', health_check, name='health_check'),
    path('api/users/', include('users.urls')),
    path('', root_view),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
