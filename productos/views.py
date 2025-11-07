import json
from decimal import Decimal, InvalidOperation

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .models import Categoria, Producto


def _parse_decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _clean_payload(payload):
    errors = {}
    nombre = str(payload.get("nombre", "")).strip()
    if not nombre:
        errors["nombre"] = "El nombre es obligatorio."

    precio = _parse_decimal(payload.get("precio"))
    if precio is None:
        errors["precio"] = "El precio debe ser un número válido."

    stock = _parse_int(payload.get("stock"))
    if stock is None or stock < 0:
        errors["stock"] = "El stock debe ser un entero mayor o igual a cero."

    descripcion = payload.get("descripcion", "")
    imagen = payload.get("imagen", "").strip()
    categoria = None
    categoria_raw = payload.get("categoria")
    if categoria_raw in ("", None):
        errors["categoria"] = "Selecciona una categoría."
    else:
        try:
            categoria_id = int(categoria_raw)
            categoria = Categoria.objects.get(id=categoria_id)
        except (TypeError, ValueError, Categoria.DoesNotExist):
            errors["categoria"] = "La categoría seleccionada no existe."

    data = {
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio,
        "stock": stock,
        "imagen": imagen,
        "categoria": categoria,
    }
    return data, errors


def _serialize_producto(producto):
    categoria = None
    if producto.categoria:
        categoria = {
            "id": producto.categoria_id,
            "nombre": producto.categoria.nombre,
        }

    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "precio": str(producto.precio),
        "stock": producto.stock,
        "imagen": producto.imagen,
        "categoria": categoria,
    }


@ensure_csrf_cookie
def panel_productos(request):
    categorias = list(Categoria.objects.all().order_by("nombre").values("id", "nombre"))
    return render(
        request,
        "productos/panel.html",
        {
            "categorias": categorias,
        },
    )


# Aqui se usan APIs
@csrf_protect
@require_http_methods(["GET", "POST"])
def api_productos(request):
    if request.method == "GET":
        productos = Producto.objects.all().order_by("-id")
        data = [_serialize_producto(producto) for producto in productos]
        return JsonResponse({"results": data})

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    data, errors = _clean_payload(payload)
    if errors:
        return JsonResponse({"errors": errors}, status=400)

    producto = Producto.objects.create(**data)
    return JsonResponse(_serialize_producto(producto), status=201)


# Aqui se usan APIs
@csrf_protect
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def api_producto_detalle(request, pid):
    producto = get_object_or_404(Producto, id=pid)

    if request.method == "GET":
        return JsonResponse(_serialize_producto(producto))

    if request.method in {"PUT", "PATCH"}:
        try:
            payload = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido."}, status=400)

        data, errors = _clean_payload(payload)
        if errors:
            return JsonResponse({"errors": errors}, status=400)

        for field, value in data.items():
            setattr(producto, field, value)
        producto.save()
        return JsonResponse(_serialize_producto(producto))

    producto.delete()
    return HttpResponse(status=204)


# Aqui se usan APIs
@csrf_protect
@require_http_methods(["GET", "POST"])
def api_categorias(request):
    if request.method == "GET":
        categorias = list(Categoria.objects.all().order_by("nombre").values("id", "nombre"))
        return JsonResponse({"results": categorias})

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    nombre = str(payload.get("nombre", "")).strip()
    if not nombre:
        return JsonResponse({"errors": {"nombre": "El nombre es obligatorio."}}, status=400)

    categoria, created = Categoria.objects.get_or_create(nombre=nombre)
    status_code = 201 if created else 200
    return JsonResponse({"id": categoria.id, "nombre": categoria.nombre}, status=status_code)
