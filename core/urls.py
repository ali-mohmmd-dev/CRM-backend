from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from core.views import RegisterOrganizationView, CustomTokenObtainPairView, CreateUserView, CurrentUserView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication (JWT)
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Registration
    path('api/register/', RegisterOrganizationView.as_view(), name='register_organization'),
    
    # Internal User Creation
    path('api/users/', CreateUserView.as_view(), name='create_user'),
    path('api/me/', CurrentUserView.as_view(), name='current_user'),
    path('api/', include('core.urls')),
    
    # Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
