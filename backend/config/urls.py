from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from users.views import CustomAuthToken
from django.http import HttpResponse
from incidents.views import health_check

def root_view(request):
    return HttpResponse("Backend incident system running. Go to /admin or /api/...", status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/', CustomAuthToken.as_view()),
    path('api/incidents/', include('incidents.urls')),
    path('api/health/', health_check, name='health_check'),
    path('api/users/', include('users.urls')),
    path('', root_view),
]
