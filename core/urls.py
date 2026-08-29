from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import (
    CreateUserView,
    CurrentUserView,
    CustomTokenObtainPairView,
    RegisterOrganizationView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterOrganizationView.as_view(), name='register_organization'),
    path('api/users/', CreateUserView.as_view(), name='create_user'),
    path('api/me/', CurrentUserView.as_view(), name='current_user'),
    path('api/', include('staff.urls')),
    path('api/', include('works.urls')),
    path('api/', include('customers.urls')),
    path('api/', include('leads.urls')),
    path('api/', include('dashboard.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
