from django.urls import path
from .views import CustomAuthToken, UserListView, ToggleUserStatusView, ChangeUserRoleView

urlpatterns = [
    path('list/', UserListView.as_view(), name='user-list'),
    path('<int:pk>/toggle_status/', ToggleUserStatusView.as_view(), name='user-toggle-status'),
    path('<int:pk>/change_role/', ChangeUserRoleView.as_view(), name='user-change-role'),
    # Token endpoint is already in config/urls.py but we can keep it here or there.
    # config/urls.py points to CustomAuthToken directly, so we don't strictly need it here,
    # but good practice to have it.
]
