from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Legacy/static-file style URLs -> redirect to canonical view paths
    path('admission_online.html', RedirectView.as_view(url='/apply/', permanent=True)),
    path('admission.html', RedirectView.as_view(url='/info/', permanent=True)),
    path('index.html', RedirectView.as_view(url='/', permanent=True)),
    path('login.html', RedirectView.as_view(url='/login/', permanent=True)),
    # Support legacy links that include the directory plus the html file,
    # e.g. requests like `/apply/index.html` should go to canonical `/apply/`.
    path('apply/index.html', RedirectView.as_view(url='/apply/', permanent=True)),
    path('apply/admission_online.html', RedirectView.as_view(url='/apply/', permanent=True)),
    path('apply/admission.html', RedirectView.as_view(url='/info/', permanent=True)),
    path('apply/login.html', RedirectView.as_view(url='/login/', permanent=True)),
   
    path('', include('admission.urls', namespace='admission')),
]



if settings.DEBUG:
    # Serve user-uploaded media files in development. Ensure MEDIA_URL is set in settings.
    if getattr(settings, 'MEDIA_URL', None):
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # staticfiles (CSS/JS) are handled by runserver automatically when DEBUG=True
