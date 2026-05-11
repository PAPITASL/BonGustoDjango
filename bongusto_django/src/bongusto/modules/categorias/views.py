"""Vistas del modulo categorias con un estilo simple y facil de leer."""

from django.http import JsonResponse
from django.shortcuts import redirect, render

from bongusto.application.services import CategoriaService
from bongusto.domain.models import Categoria
from bongusto.modules.shared.audit import registrar_movimiento


# Servicio de categorias (aqui esta la logica fuerte)
_service = CategoriaService()


class CategoriaPageHelper:
    """Agrupa cositas para no repetir codigo en todas las vistas."""

    # Trae todas las categorias
    # Si algo falla, simplemente devuelve vacio y no rompe la vista
    def listar_categorias(self):
        try:
            return _service.listar_todas()
        except Exception:
            return []

    # Busca una categoria por id
    def buscar_categoria(self, pk):
        try:
            return _service.buscar_por_id(pk)
        except Exception:
            return None

    # Este metodo se usa para mostrar el formulario
    # sirve tanto para crear, editar o ver
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

    # Aqui tomo lo que viene del formulario y lo paso al objeto categoria
    def cargar_desde_post(self, request, categoria):
        categoria.nombre_cate = (request.POST.get("nombre_cate", "") or "").strip()
        return categoria

    # Validacion sencilla (solo que no venga vacio)
    def validar(self, request, categoria, accion):
        if not categoria.nombre_cate:
            return None, self.render_form(
                request,
                categoria,
                accion,
                error="Debes escribir el nombre de la categoria.",
            )
        return categoria, None

    # Esto es para la API (convertir a JSON)
    def categoria_to_dict(self, categoria):
        return {
            "id_cate": categoria.id_cate,
            "nombre_cate": categoria.nombre_cate or "",
        }


# Helper listo para usar en todas las vistas
_helper = CategoriaPageHelper()


# Vista principal (listado)
def index(request):
    return render(request, "categoria/index.html", {"categorias": _helper.listar_categorias()})


# Muestra formulario vacio para crear
def create(request):
    return _helper.render_form(request, Categoria(), "Crear")


# Ver categoria (solo lectura)
def ver(request, pk):
    categoria = _helper.buscar_categoria(pk)
    if not categoria:
        return redirect("/categorias")
    return _helper.render_form(request, categoria, "Ver", readonly=True)


# Guardar nueva categoria
def store(request):
    if request.method != "POST":
        return redirect("/categorias")

    # Paso datos del form al objeto
    categoria = _helper.cargar_desde_post(request, Categoria())

    # Validacion
    categoria, error = _helper.validar(request, categoria, "Crear")
    if error:
        return error

    try:
        # Guardar en BD
        _service.guardar(categoria)

        # Guardar en bitacora
        registrar_movimiento(request, f"Creacion de categoria {categoria.nombre_cate or categoria.id_cate}.")

        return redirect("/categorias")
    except Exception:
        return _helper.render_form(request, categoria, "Crear", error="No fue posible guardar la categoria.")


# Formulario para editar
def edit(request, pk):
    categoria = _helper.buscar_categoria(pk)
    if not categoria:
        return redirect("/categorias")
    return _helper.render_form(request, categoria, "Editar")


# Actualizar categoria
def update(request, pk):
    if request.method != "POST":
        return redirect("/categorias")

    categoria = _helper.buscar_categoria(pk)
    if not categoria:
        return redirect("/categorias")

    # Cargar nuevos datos
    categoria = _helper.cargar_desde_post(request, categoria)

    # Validar
    categoria, error = _helper.validar(request, categoria, "Editar")
    if error:
        return error

    try:
        # Guardar cambios
        _service.guardar(categoria)

        # Registrar en bitacora
        registrar_movimiento(request, f"Actualizacion de categoria {categoria.nombre_cate or categoria.id_cate}.")

        return redirect("/categorias")
    except Exception:
        return _helper.render_form(request, categoria, "Editar", error="No fue posible actualizar la categoria.")


# Eliminar categoria
def delete(request, pk):
    try:
        categoria = _helper.buscar_categoria(pk)

        _service.eliminar(pk)

        # Si existia, lo registro
        if categoria:
            registrar_movimiento(request, f"Eliminacion de categoria {categoria.nombre_cate or categoria.id_cate}.")
    except Exception:
        # Si algo falla, simplemente sigue
        pass

    return redirect("/categorias")


# API para listar categorias
def api_listar(request):
    if request.method != "GET":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    categorias = _helper.listar_categorias()

    return JsonResponse(
        [_helper.categoria_to_dict(categoria) for categoria in categorias],
        safe=False
    )