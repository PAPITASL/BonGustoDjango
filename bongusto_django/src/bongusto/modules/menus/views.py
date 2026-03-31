"""Vistas del modulo menus en un estilo simple."""

from collections import defaultdict

from django.core.cache import cache
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from bongusto.application.services import MenuService
from bongusto.domain.models import Menu, PedidoDetalle, Producto
from bongusto.infrastructure.pdf_generator import crear_pdf_compuesto
from bongusto.modules.shared.audit import registrar_movimiento
from bongusto.modules.shared.excel_import import leer_filas_excel, texto_limpio


_service = MenuService()


class MenuPageHelper:
    def leer_filtros(self, request):
        return {
            "nombre": request.GET.get("nombre", ""),
            "descripcion": request.GET.get("descripcion", ""),
            "creados": request.GET.get("creados", ""),
            "repetidos": request.GET.get("repetidos", ""),
        }

    def listar_filtrado(self, filtros=None):
        filtros = filtros or {"nombre": "", "descripcion": ""}
        try:
            return _service.listar_filtrado(filtros.get("nombre", ""), filtros.get("descripcion", ""))
        except Exception:
            return []

    def listar_todos(self):
        try:
            return _service.listar_todos()
        except Exception:
            return []

    def buscar(self, pk):
        try:
            return _service.buscar_por_id(pk)
        except Exception:
            return None

    def render_form(self, request, menu, accion, readonly=False, error=""):
        return render(request, "menu/form.html", {"menu": menu, "accion": accion, "readonly": readonly, "error": error})

    def render_index(self, request, menus, filtros, error=""):
        mensaje = ""
        if filtros.get("creados") or filtros.get("repetidos"):
            mensaje = f"Importacion completada. Nuevos: {filtros.get('creados') or 0}. Repetidos detectados: {filtros.get('repetidos') or 0}."

        return render(
            request,
            "menu/index.html",
            {
                "menus": menus,
                "filtros": {"nombre": filtros.get("nombre", ""), "descripcion": filtros.get("descripcion", "")},
                "mensaje": mensaje,
                "error": error,
            },
        )

    def cargar_desde_post(self, request, menu):
        menu.nombre_menu = (request.POST.get("nombre_menu", "") or "").strip()
        menu.descripcion_menu = (request.POST.get("descripcion_menu", "") or "").strip()
        return menu

    def validar(self, request, menu, accion):
        if not menu.nombre_menu:
            return None, self.render_form(request, menu, accion, error="Debes escribir el nombre del menu.")
        return menu, None

    def construir_reporte(self, menus):
        menus = list(menus)
        menu_ids = [menu.id_menu for menu in menus]
        productos = list(Producto.objects.select_related("id_cate").filter(id_menu_id__in=menu_ids))
        productos_por_menu = defaultdict(list)
        productos_index = {}

        for producto in productos:
            if producto.id_menu_id:
                productos_por_menu[producto.id_menu_id].append(producto)
            productos_index[producto.id_producto] = producto

        ventas_por_menu = defaultdict(int)
        ventas_por_categoria = defaultdict(int)

        for detalle in PedidoDetalle.objects.filter(id_producto__in=list(productos_index.keys())).only("id_producto", "cantidad"):
            producto = productos_index.get(int(detalle.id_producto)) if detalle.id_producto is not None else None
            if not producto:
                continue
            cantidad = detalle.cantidad or 0
            ventas_por_menu[producto.id_menu_id] += cantidad
            categoria = producto.id_cate.nombre_cate if producto.id_cate else "Sin categoria"
            ventas_por_categoria[categoria] += cantidad

        activos = 0
        desactivados = 0
        tabla_principal = []
        ranking = []

        for menu in menus:
            productos_menu = productos_por_menu.get(menu.id_menu, [])
            total_productos = len(productos_menu)
            total_activos = sum(1 for producto in productos_menu if (producto.estado or "").lower() == "activo")
            estado_menu = "Activo" if total_activos > 0 else "Desactivado"
            if estado_menu == "Activo":
                activos += 1
            else:
                desactivados += 1

            vendidos = ventas_por_menu.get(menu.id_menu, 0)
            categorias = sorted({p.id_cate.nombre_cate for p in productos_menu if p.id_cate and p.id_cate.nombre_cate})

            tabla_principal.append([str(menu.id_menu), menu.nombre_menu or "-", menu.descripcion_menu or "-", str(total_productos), estado_menu, ", ".join(categorias[:3]) if categorias else "Sin categoria"])
            ranking.append([menu.nombre_menu or f"Menu {menu.id_menu}", str(vendidos), str(total_productos), estado_menu])

        ranking.sort(key=lambda row: int(row[1]), reverse=True)
        categorias_rows = [[categoria, str(total)] for categoria, total in sorted(ventas_por_categoria.items(), key=lambda item: item[1], reverse=True)] or [["Sin categorias con ventas", "0"]]
        top_tipo = categorias_rows[0][0] if categorias_rows else "Sin datos"
        top_total = categorias_rows[0][1] if categorias_rows else "0"

        return [
            {
                "heading": "Tabla menus, estado, categorias y actividad",
                "headers": ["ID", "Menu", "Descripcion", "Productos", "Estado", "Categorias"],
                "rows": tabla_principal or [["-", "Sin menus", "-", "0", "-", "-"]],
                "col_widths": [1.5 * 72 / 2.54, 4.0 * 72 / 2.54, 7.3 * 72 / 2.54, 2.2 * 72 / 2.54, 2.5 * 72 / 2.54, 6.0 * 72 / 2.54],
            },
            {
                "heading": "Menus mas consultados",
                "paragraph": "Se estima con la cantidad total vendida de productos asociados a cada menu.",
                "headers": ["Menu", "Ventas", "Productos", "Estado"],
                "rows": ranking[:10] or [["Sin menus", "0", "0", "-"]],
            },
            {
                "heading": "Categorias mas populares (bebidas, entradas, etc.)",
                "paragraph": "Calculado por cantidad vendida en pedidos.",
                "headers": ["Categoria", "Ventas"],
                "rows": categorias_rows,
            },
            {
                "heading": "Menus activos vs desactivados",
                "paragraph": "Un menu se considera activo cuando tiene al menos un producto activo asociado.",
                "headers": ["Estado", "Total"],
                "rows": [["Activos", str(activos)], ["Desactivados", str(desactivados)]],
            },
            {
                "heading": "Que tipo de comida vende mas",
                "headers": ["Tipo de comida lider", "Ventas"],
                "rows": [[top_tipo, str(top_total)]],
            },
        ]

    def menu_to_dict(self, menu):
        return {"id_menu": menu.id_menu, "nombre_menu": menu.nombre_menu or "", "descripcion_menu": menu.descripcion_menu or ""}


_helper = MenuPageHelper()


def index(request):
    filtros = _helper.leer_filtros(request)
    return _helper.render_index(request, _helper.listar_filtrado(filtros), filtros)


def create(request):
    return _helper.render_form(request, Menu(), "Crear")


def ver(request, pk):
    menu = _helper.buscar(pk)
    if not menu:
        return redirect("/menus")
    return _helper.render_form(request, menu, "Ver", readonly=True)


def store(request):
    if request.method != "POST":
        return redirect("/menus")

    menu = _helper.cargar_desde_post(request, Menu())
    menu, error = _helper.validar(request, menu, "Crear")
    if error:
        return error

    try:
        _service.guardar(menu)
        registrar_movimiento(request, f"Creacion de menu {menu.nombre_menu or menu.id_menu}.")
        return redirect("/menus")
    except Exception:
        return _helper.render_form(request, menu, "Crear", error="No fue posible guardar el menu.")


def edit(request, pk):
    menu = _helper.buscar(pk)
    if not menu:
        return redirect("/menus")
    return _helper.render_form(request, menu, "Editar")


def update(request, pk):
    if request.method != "POST":
        return redirect("/menus")

    menu = _helper.buscar(pk)
    if not menu:
        return redirect("/menus")

    menu = _helper.cargar_desde_post(request, menu)
    menu, error = _helper.validar(request, menu, "Editar")
    if error:
        return error

    try:
        _service.guardar(menu)
        registrar_movimiento(request, f"Actualizacion de menu {menu.nombre_menu or menu.id_menu}.")
        return redirect("/menus")
    except Exception:
        return _helper.render_form(request, menu, "Editar", error="No fue posible actualizar el menu.")


def delete(request, pk):
    try:
        menu = _helper.buscar(pk)
        _service.eliminar(pk)
        if menu:
            registrar_movimiento(request, f"Eliminacion de menu {menu.nombre_menu or menu.id_menu}.")
        return redirect("/menus")
    except Exception:
        filtros = {"nombre": "", "descripcion": "", "creados": "", "repetidos": ""}
        return _helper.render_index(request, _helper.listar_filtrado(), filtros, error="No se puede eliminar este menu porque tiene productos asociados.")


def importar_excel(request):
    if request.method != "POST":
        return redirect("/menus")

    try:
        filas = leer_filas_excel(request.FILES.get("archivo_excel"))
        total_importados = 0
        total_repetidos = 0
        errores = []

        with transaction.atomic():
            for indice, fila in enumerate(filas, start=2):
                nombre = texto_limpio(fila.get("nombre_menu") or fila.get("menu") or fila.get("item") or fila.get("nombre"))
                descripcion = texto_limpio(fila.get("descripcion_menu") or fila.get("descripcion"))

                if not nombre:
                    errores.append(f"Fila {indice}: falta el nombre del menu.")
                    continue

                menu_existente = Menu.objects.filter(nombre_menu__iexact=nombre).first()
                if menu_existente:
                    total_repetidos += 1

                menu = menu_existente or Menu()
                menu.nombre_menu = nombre
                menu.descripcion_menu = descripcion
                _service.guardar(menu)
                total_importados += 1

        if total_importados == 0:
            detalle = f" Detalle: {errores[0]}" if errores else ""
            raise ValueError("No se importo ningun menu. Revisa encabezados y filas del archivo." + detalle)

        registrar_movimiento(request, f"Importacion masiva de {total_importados} menus desde archivo Excel.")
        nuevos = total_importados - total_repetidos
        return redirect(f"/menus?creados={nuevos}&repetidos={total_repetidos}")
    except Exception as exc:
        filtros = {"nombre": "", "descripcion": "", "creados": "", "repetidos": ""}
        return _helper.render_index(request, _helper.listar_filtrado(), filtros, error=str(exc))


def pdf(request):
    try:
        filtros = _helper.leer_filtros(request)
        menus = _helper.listar_filtrado(filtros)
        data = crear_pdf_compuesto("Reporte de Menus", _helper.construir_reporte(menus))
        response = HttpResponse(data, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="reporte_menus.pdf"'
        return response
    except Exception:
        return HttpResponse("No fue posible generar el reporte de menus.", status=500)


def api_listar(request):
    if request.method != "GET":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    cache_key = "api:menus:listar:v1"
    cached = cache.get(cache_key)
    if cached is not None:
        response = JsonResponse(cached, safe=False)
        response["X-Cache-Hit"] = "1"
        return response

    data = [_helper.menu_to_dict(menu) for menu in _helper.listar_todos()]
    cache.set(cache_key, data, timeout=300)
    response = JsonResponse(data, safe=False)
    response["X-Cache-Hit"] = "0"
    return response
