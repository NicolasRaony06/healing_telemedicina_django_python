from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("usuarios/", include("usuarios.urls")),
    path("medicos/", include("medico.urls")),
    path("pacientes/", include("paciente.urls")),
    path("", views.index_html),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
