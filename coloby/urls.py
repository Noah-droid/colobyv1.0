from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework_swagger.views import get_swagger_view
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="Coloby API",
        default_version='v1',),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/accounts/", include('accounts.urls')),
    path("api/v1/", include('cowork.urls')),
    path('views', TemplateView.as_view(template_name='index.html')),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0),name='schema-swagger-ui'),
    path("accounts/", include("allauth.urls")),

    # Notifications
    # path('^notifications/', include('notifications_rest.urls')),

    # DEBUG_TOOL_BAR
    # path("__debug__/", include("debug_toolbar.urls")),
        
    # path('docs/', schema_view.with_ui('swagger', cache_timeout=0),name='schema-swagger-ui'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

