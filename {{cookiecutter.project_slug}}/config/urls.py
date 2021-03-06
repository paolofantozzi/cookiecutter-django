# -*- coding: utf-8 -*-

"""Entry point for celery app."""

from django.conf import settings
from django.conf.urls.static import static
{%- if cookiecutter.api_only_mode == 'n' %}
from django.contrib import admin
{%- endif %}
{%- if cookiecutter.use_async == 'y' %}
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
{%- endif %}
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
{%- if cookiecutter.api_only_mode == 'y' %}
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularRedocView
from drf_spectacular.views import SpectacularSwaggerView
{%- else %}
from django.views.generic import TemplateView
{%- endif %}
{%- if cookiecutter.use_drf == 'y' and cookiecutter.api_only_mode == 'n' %}
from rest_framework.authtoken.views import obtain_auth_token
{%- endif %}

urlpatterns = [
    {%- if cookiecutter.api_only_mode == 'y' %}
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='schema-swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='schema-redoc'),
    path('api/users/', include('{{ cookiecutter.project_slug }}.users.urls', namespace='users')),
    {%- elif cookiecutter.use_drf == 'y' %}
    # API base url
    path('api/', include('config.api_router')),
    # DRF auth token
    path('auth-token/', obtain_auth_token),
    {%- else %}
    path('', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    path(
        'about/', TemplateView.as_view(template_name='pages/about.html'), name='about'
    ),
    # Django Admin, use {% raw %}{% url 'admin:index' %}{% endraw %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path('users/', include('{{ cookiecutter.project_slug }}.users.urls', namespace='users')),
    path('accounts/', include('allauth.urls')),
    {%- endif %}
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

{%- if cookiecutter.use_async == 'y' %}
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()
{%- endif %}

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            '400/',
            default_views.bad_request,
            kwargs={'exception': Exception('Bad Request!')},
        ),
        path(
            '403/',
            default_views.permission_denied,
            kwargs={'exception': Exception('Permission Denied')},
        ),
        path(
            '404/',
            default_views.page_not_found,
            kwargs={'exception': Exception('Page not Found')},
        ),
        path('500/', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
