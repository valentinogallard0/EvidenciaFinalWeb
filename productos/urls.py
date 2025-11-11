from django.urls import path

from . import views

urlpatterns = [
    path("", views.panel_productos, name="panel_productos"),
    path("admin-productos/", views.panel_productos),
    path("categorias/", views.panel_categorias, name="panel_categorias"),
    path("catalogo/", views.panel_catalogo, name="panel_catalogo"),
    # Endpoints REST consumidos por panel.html
    path("api/productos/", views.api_productos, name="api_productos"),
    path("api/productos/<int:pid>/", views.api_producto_detalle, name="api_producto_detalle"),
    path("api/categorias/", views.api_categorias, name="api_categorias"),
]
