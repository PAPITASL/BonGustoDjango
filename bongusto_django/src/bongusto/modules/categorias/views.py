"""Vistas del modulo categorias con un estilo simple y facil de leer."""

from django.http import JsonResponse
from django.shortcuts import redirect, render

from bongusto.application.services import CategoriaService
from bongusto.domain.models import Categoria
from bongusto.modules.shared.audit import registrar_movimiento


_service = CategoriaService()


class CategoriaPageHelper:
    """Agrupa pasos pequeños para evitar repetir codigo."""

    def listar_categorias(self):
        try:
            return _service.listar_todas()
        except Exception:
            return []

    def buscar_categoria(self, pk):
        try:
            return _service.buscar_por_id(pk)
        except Exception:
            return None

    def render_form(self, request, categoria, accion, readonly=False, error=""):
        return render(
            request,
            "categoria/form.html",
            {
                "categoria": categoria,
                "accion": accion,
                "readonly": readonly,
                "error": error,
            },
        )

    def cargar_desde_post(self, request, categoria):
        categoria.nombre_cate = (request.POST.get("nombre_cate", "") or "").strip()
        return categoria

    def validar(self, request, categoria, accion):
        if not categoria.nombre_cate:
            return None, self.render_form(
                request,
                categoria,
                accion,
                error="Debes escribir el nombre de la categoria.",
            )
        return categoria, None

    def categoria_to_dict(self, categoria):
        return {
            "id_cate": categoria.id_cate,
            "nombre_cate": categoria.nombre_cate or "",
        }


_helper = CategoriaPageHelper()


def index(request):
    return render(request, "categoria/index.html", {"categorias": _helper.listar_categorias()})


def create(request):
    return _helper.render_form(request, Categoria(), "Crear")


def ver(request, pk):
    categoria = _helper.buscar_categoria(pk)
    if not categoria:
        return redirect("/categorias")
    return _helper.render_form(request, categoria, "Ver", readonly=True)


def store(request):
    if request.method != "POST":
        return redirect("/categorias")

    categoria = _helper.cargar_desde_post(request, Categoria())
    categoria, error = _helper.validar(request, categoria, "Crear")
    if error:
        return error

    try:
        _service.guardar(categoria)
        registrar_movimiento(request, f"Creacion de categoria {categoria.nombre_cate or categoria.id_cate}.")
        return redirect("/categorias")
    except Exception:
        return _helper.render_form(request, categoria, "Crear", error="No fue posible guardar la categoria.")


def edit(request, pk):
    categoria = _helper.buscar_categoria(pk)
    if not categoria:
        return redirect("/categorias")
    return _helper.render_form(request, categoria, "Editar")


def update(request, pk):
    if request.method != "POST":
        return redirect("/categorias")

    categoria = _helper.buscar_categoria(pk)
    if not categoria:
        return redirect("/categorias")

    categoria = _helper.cargar_desde_post(request, categoria)
    categoria, error = _helper.validar(request, categoria, "Editar")
    if error:
        return error

    try:
        _service.guardar(categoria)
        registrar_movimiento(request, f"Actualizacion de categoria {categoria.nombre_cate or categoria.id_cate}.")
        return redirect("/categorias")
    except Exception:
        return _helper.render_form(request, categoria, "Editar", error="No fue posible actualizar la categoria.")


def delete(request, pk):
    try:
        categoria = _helper.buscar_categoria(pk)
        _service.eliminar(pk)
        if categoria:
            registrar_movimiento(request, f"Eliminacion de categoria {categoria.nombre_cate or categoria.id_cate}.")
    except Exception:
        pass
    return redirect("/categorias")


def api_listar(request):
    if request.method != "GET":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    categorias = _helper.listar_categorias()
    return JsonResponse([_helper.categoria_to_dict(categoria) for categoria in categorias], safe=False)
