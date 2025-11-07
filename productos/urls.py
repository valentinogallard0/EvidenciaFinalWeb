from django.urls import path

from . import views

urlpatterns = [
    path("", views.panel_productos, name="panel_productos"),
    path("admin-productos/", views.panel_productos),
    # Aqui se usan APIs
    path("api/productos/", views.api_productos, name="api_productos"),
    path("api/productos/<int:pid>/", views.api_producto_detalle, name="api_producto_detalle"),
    # Aqui se usan APIs
    path("api/categorias/", views.api_categorias, name="api_categorias"),
]
