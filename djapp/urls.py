from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [

    path('admin/', admin.site.urls),
    # society_app
    path('', include('djproject.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
