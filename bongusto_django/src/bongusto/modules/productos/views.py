"""Vistas del modulo productos en un estilo simple."""

from collections import defaultdict
from decimal import Decimal, InvalidOperation

from django.core.cache import cache
from django.db import transaction
from django.db.models import Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from bongusto.application.services import CategoriaService, MenuService, ProductoService
from bongusto.domain.models import PedidoDetalle, Producto
from bongusto.infrastructure.pdf_generator import crear_pdf_compuesto
from bongusto.modules.shared.audit import registrar_movimiento
from bongusto.modules.shared.excel_import import leer_filas_excel, texto_limpio


_service = ProductoService()
_menu_service = MenuService()
_cat_service = CategoriaService()


class ProductoPageHelper:
    def listar_menus(self):
        try:
            return _menu_service.listar_todos()
        except Exception:
            return []

    def listar_categorias(self):
        try:
            return _cat_service.listar_todas()
        except Exception:
            return []

    def listar_filtrado(self, filtros=None):
        filtros = filtros or {"nombre": "", "categoria": "", "menu": "", "precio_min": "", "precio_max": ""}
        try:
            return _service.listar_filtrado(filtros.get("nombre", ""), filtros.get("categoria", ""), filtros.get("menu", ""), filtros.get("precio_min", ""), filtros.get("precio_max", ""))
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

    def leer_filtros(self, request):
        return {
            "nombre": request.GET.get("nombre", ""),
            "categoria": request.GET.get("categoria", ""),
            "menu": request.GET.get("menu", ""),
            "precio_min": request.GET.get("precio_min", ""),
            "precio_max": request.GET.get("precio_max", ""),
            "creados": request.GET.get("creados", ""),
            "repetidos": request.GET.get("repetidos", ""),
        }

    def render_form(self, request, producto, accion, error=""):
        return render(
            request,
            "producto/form.html",
            {
                "producto": producto,
                "menus": self.listar_menus(),
                "categorias": self.listar_categorias(),
                "accion": accion,
                "readonly": accion == "Ver",
                "error": error,
            },
        )

    def render_index(self, request, productos, filtros, error=""):
        mensaje = ""
        if filtros.get("creados") or filtros.get("repetidos"):
            mensaje = f"Importacion completada. Nuevos: {filtros.get('creados') or 0}. Repetidos detectados: {filtros.get('repetidos') or 0}."

        return render(
            request,
            "producto/index.html",
            {
                "productos": productos,
                "menus": self.listar_menus(),
                "filtros": {
                    "nombre": filtros.get("nombre", ""),
                    "categoria": filtros.get("categoria", ""),
                    "menu": filtros.get("menu", ""),
                    "precio_min": filtros.get("precio_min", ""),
                    "precio_max": filtros.get("precio_max", ""),
                },
                "mensaje": mensaje,
                "error": error,
            },
        )

    def parse_precio(self, valor):
        try:
            precio = Decimal(str(valor).strip())
        except (InvalidOperation, AttributeError, TypeError):
            return None
        if precio <= 0:
            return None
        return precio

    def cargar_desde_post(self, request, producto):
        producto.nombre_producto = (request.POST.get("nombre_producto", "") or "").strip()
        producto.descripcion_producto = (request.POST.get("descripcion_producto", "") or "").strip()
        producto.estado = (request.POST.get("estado", "activo") or "").strip()
        return producto

    def asignar_relaciones(self, menu_id, cat_id, producto):
        producto.id_menu = _menu_service.buscar_por_id(menu_id) if menu_id else None
        producto.id_cate = _cat_service.buscar_por_id(cat_id) if cat_id else None
        return producto

    def validar(self, request, producto, accion, menu_id, cat_id, precio):
        if not producto.nombre_producto:
            return None, self.render_form(request, producto, accion, "Debes ingresar el nombre del producto.")
        if not producto.descripcion_producto:
            return None, self.render_form(request, producto, accion, "Debes ingresar la descripcion del producto.")
        if precio is None:
            return None, self.render_form(request, producto, accion, "El precio debe ser mayor que cero.")
        if not menu_id:
            return None, self.render_form(request, producto, accion, "Debes seleccionar un menu.")
        if not cat_id:
            return None, self.render_form(request, producto, accion, "Debes seleccionar una categoria.")
        return producto, None

    def money(self, value):
        if value in (None, ""):
            return "$0.00"
        return f"${value}"

    def construir_reporte(self, productos):
        productos = list(productos)
        producto_ids = [p.id_producto for p in productos]
        detalles = list(PedidoDetalle.objects.filter(id_producto__in=producto_ids).only("id_producto", "cantidad", "precio"))

        ventas_por_producto = defaultdict(int)
        ingresos_por_producto = defaultdict(float)
        for detalle in detalles:
            if detalle.id_producto is None:
                continue
            producto_id = int(detalle.id_producto)
            cantidad = detalle.cantidad or 0
            precio_unitario = float(detalle.precio or 0)
            ventas_por_producto[producto_id] += cantidad
            ingresos_por_producto[producto_id] += cantidad * precio_unitario

        tabla_principal = []
        ranking_vendidos = []
        ranking_menos = []
        ingresos_rows = []
        agotados_rows = []

        for producto in productos:
            categoria = producto.id_cate.nombre_cate if producto.id_cate else "Sin categoria"
            menu_nombre = producto.id_menu.nombre_menu if producto.id_menu else "-"
            estado = producto.estado or "-"
            vendidos = ventas_por_producto.get(producto.id_producto, 0)
            ingresos = ingresos_por_producto.get(producto.id_producto, 0)

            tabla_principal.append([str(producto.id_producto), producto.nombre_producto or "-", self.money(producto.precio_producto), categoria, menu_nombre, estado, str(vendidos)])
            ranking_vendidos.append([producto.nombre_producto or f"Producto {producto.id_producto}", str(vendidos), self.money(round(ingresos, 2))])
            ranking_menos.append([producto.nombre_producto or f"Producto {producto.id_producto}", str(vendidos), estado])
            ingresos_rows.append([producto.nombre_producto or f"Producto {producto.id_producto}", self.money(round(ingresos, 2)), str(vendidos)])

            if (estado or "").lower() != "activo" or vendidos == 0:
                agotados_rows.append([producto.nombre_producto or f"Producto {producto.id_producto}", estado, str(vendidos), "Revisar disponibilidad"])

        ranking_vendidos.sort(key=lambda row: (int(row[1]), row[0]), reverse=True)
        ranking_menos.sort(key=lambda row: (int(row[1]), row[0]))
        ingresos_rows.sort(key=lambda row: float(row[1].replace("$", "")), reverse=True)
        agotados_rows.sort(key=lambda row: (row[1] != "inactivo", int(row[2])))

        promedio_categoria_rows = [
            [item["id_cate__nombre_cate"] or "Sin categoria", self.money(item["promedio"] or 0)]
            for item in (
                Producto.objects.filter(id_producto__in=producto_ids)
                .values("id_cate__nombre_cate")
                .annotate(promedio=Avg("precio_producto"))
                .order_by("id_cate__nombre_cate")
            )
        ] or [["Sin categorias", "$0.00"]]

        return [
            {
                "heading": "Tabla productos, categorias, menus y actividad",
                "headers": ["ID", "Producto", "Precio", "Categoria", "Menu", "Estado", "Ventas"],
                "rows": tabla_principal or [["-", "Sin productos", "-", "-", "-", "-", "0"]],
                "col_widths": [1.2 * 72 / 2.54, 4.8 * 72 / 2.54, 2.2 * 72 / 2.54, 3.8 * 72 / 2.54, 3.8 * 72 / 2.54, 2.1 * 72 / 2.54, 1.9 * 72 / 2.54],
            },
            {
                "heading": "Productos mas vendidos",
                "paragraph": "Calculado por cantidad total registrada en pedido_detalle.",
                "headers": ["Producto", "Ventas", "Ingresos"],
                "rows": ranking_vendidos[:10] or [["Sin productos", "0", "$0.00"]],
            },
            {
                "heading": "Productos menos vendidos",
                "paragraph": "Incluye productos sin ventas registradas.",
                "headers": ["Producto", "Ventas", "Estado"],
                "rows": ranking_menos[:10] or [["Sin productos", "0", "-"]],
            },
            {
                "heading": "Ingresos por producto",
                "headers": ["Producto", "Ingresos", "Ventas"],
                "rows": ingresos_rows[:10] or [["Sin productos", "$0.00", "0"]],
            },
            {
                "heading": "Productos agotados (stock bajo)",
                "paragraph": "Como el modelo no guarda stock real, se listan productos inactivos o sin ventas para revision.",
                "headers": ["Producto", "Estado", "Ventas", "Observacion"],
                "rows": agotados_rows[:10] or [["Sin alertas", "-", "0", "Todo en orden"]],
            },
            {
                "heading": "Precio promedio por categoria",
                "headers": ["Categoria", "Precio promedio"],
                "rows": promedio_categoria_rows,
            },
        ]

    def producto_to_dict(self, producto):
        return {
            "id_producto": producto.id_producto,
            "nombre_producto": producto.nombre_producto or "",
            "descripcion_producto": producto.descripcion_producto or "",
            "precio_producto": float(producto.precio_producto or 0),
            "estado": producto.estado or "",
            "id_menu": producto.id_menu_id,
            "nombre_menu": producto.id_menu.nombre_menu if producto.id_menu else "",
            "id_cate": producto.id_cate_id,
            "nombre_cate": producto.id_cate.nombre_cate if producto.id_cate else "",
        }


_helper = ProductoPageHelper()


def index(request):
    filtros = _helper.leer_filtros(request)
    return _helper.render_index(request, _helper.listar_filtrado(filtros), filtros)


def create(request):
    return _helper.render_form(request, Producto(), "Crear")


def ver(request, pk):
    producto = _helper.buscar(pk)
    if not producto:
        return redirect("/productos")
    return _helper.render_form(request, producto, "Ver")


def store(request):
    if request.method != "POST":
        return redirect("/productos")

    producto = _helper.cargar_desde_post(request, Producto())
    menu_id = request.POST.get("id_menu")
    cat_id = request.POST.get("id_cate")
    precio = _helper.parse_precio(request.POST.get("precio_producto"))
    producto, error = _helper.validar(request, producto, "Crear", menu_id, cat_id, precio)
    if error:
        return error

    producto.precio_producto = precio
    producto = _helper.asignar_relaciones(menu_id, cat_id, producto)

    try:
        _service.guardar(producto)
        registrar_movimiento(request, f"Creacion de producto {producto.nombre_producto or producto.id_producto}.")
        return redirect("/productos")
    except Exception:
        return _helper.render_form(request, producto, "Crear", "No fue posible guardar el producto.")


def edit(request, pk):
    producto = _helper.buscar(pk)
    if not producto:
        return redirect("/productos")
    return _helper.render_form(request, producto, "Editar")


def update(request, pk):
    if request.method != "POST":
        return redirect("/productos")

    producto = _helper.buscar(pk)
    if not producto:
        return redirect("/productos")

    producto = _helper.cargar_desde_post(request, producto)
    menu_id = request.POST.get("id_menu")
    cat_id = request.POST.get("id_cate")
    precio = _helper.parse_precio(request.POST.get("precio_producto"))
    producto, error = _helper.validar(request, producto, "Editar", menu_id, cat_id, precio)
    if error:
        return error

    producto.precio_producto = precio
    producto = _helper.asignar_relaciones(menu_id, cat_id, producto)

    try:
        _service.guardar(producto)
        registrar_movimiento(request, f"Actualizacion de producto {producto.nombre_producto or producto.id_producto}.")
        return redirect("/productos")
    except Exception:
        return _helper.render_form(request, producto, "Editar", "No fue posible actualizar el producto.")


def delete(request, pk):
    try:
        producto = _helper.buscar(pk)
        _service.eliminar(pk)
        if producto:
            registrar_movimiento(request, f"Eliminacion de producto {producto.nombre_producto or producto.id_producto}.")
    except Exception:
        pass
    return redirect("/productos")


def importar_excel(request):
    if request.method != "POST":
        return redirect("/productos")

    try:
        filas = leer_filas_excel(request.FILES.get("archivo_excel"))
        total_importados = 0
        total_repetidos = 0
        errores = []

        with transaction.atomic():
            for indice, fila in enumerate(filas, start=2):
                nombre = texto_limpio(fila.get("nombre_producto") or fila.get("producto") or fila.get("nombre"))
                descripcion = texto_limpio(fila.get("descripcion_producto") or fila.get("descripcion"))
                menu_nombre = texto_limpio(fila.get("menu") or fila.get("nombre_menu"))
                categoria_nombre = texto_limpio(fila.get("categoria") or fila.get("nombre_cate"))
                estado = texto_limpio(fila.get("estado") or "activo").lower() or "activo"
                precio = _helper.parse_precio(fila.get("precio_producto") or fila.get("precio"))

                if not nombre:
                    errores.append(f"Fila {indice}: falta el nombre del producto.")
                    continue
                if precio is None:
                    errores.append(f"Fila {indice}: el precio debe ser mayor que cero.")
                    continue
                if not descripcion or not menu_nombre or not categoria_nombre:
                    errores.append(f"Fila {indice}: faltan descripcion, menu o categoria.")
                    continue

                menu_obj = _menu_service.listar_todos().filter(nombre_menu__iexact=menu_nombre).first()
                if not menu_obj:
                    from bongusto.domain.models import Menu
                    menu_obj = Menu(nombre_menu=menu_nombre, descripcion_menu="")
                    menu_obj.save()

                from bongusto.domain.models import Categoria
                categoria_obj = Categoria.objects.filter(nombre_cate__iexact=categoria_nombre).first()
                if not categoria_obj:
                    categoria_obj = Categoria(nombre_cate=categoria_nombre)
                    categoria_obj.save()

                producto_existente = Producto.objects.filter(nombre_producto__iexact=nombre).first()
                if producto_existente:
                    total_repetidos += 1

                producto = producto_existente or Producto()
                producto.nombre_producto = nombre
                producto.descripcion_producto = descripcion
                producto.precio_producto = precio
                producto.id_menu = menu_obj
                producto.id_cate = categoria_obj
                producto.estado = estado if estado in {"activo", "inactivo"} else "activo"
                _service.guardar(producto)
                total_importados += 1

        if total_importados == 0:
            detalle = f" Detalle: {errores[0]}" if errores else ""
            raise ValueError("No se importo ningun producto. Revisa encabezados y filas del archivo." + detalle)

        registrar_movimiento(request, f"Importacion masiva de {total_importados} productos desde archivo Excel.")
        nuevos = total_importados - total_repetidos
        return redirect(f"/productos?creados={nuevos}&repetidos={total_repetidos}")
    except Exception as exc:
        filtros = {"nombre": "", "categoria": "", "menu": "", "precio_min": "", "precio_max": "", "creados": "", "repetidos": ""}
        return _helper.render_index(request, _helper.listar_filtrado(), filtros, error=str(exc))


def reporte(request):
    try:
        filtros = _helper.leer_filtros(request)
        productos = _helper.listar_filtrado(filtros)
        pdf = crear_pdf_compuesto("Reporte de Productos", _helper.construir_reporte(productos))
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="reporte_productos.pdf"'
        return response
    except Exception:
        return HttpResponse("No fue posible generar el reporte de productos.", status=500)


def api_listar(request):
    if request.method != "GET":
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

    categoria_id = request.GET.get("categoria_id", "").strip()
    menu_id = request.GET.get("menu_id", "").strip()
    solo_destacados = request.GET.get("destacados") == "1"
    cache_key = f"api:productos:listar:v1:categoria={categoria_id or '-'}:menu={menu_id or '-'}:destacados={1 if solo_destacados else 0}"
    cached = cache.get(cache_key)
    if cached is not None:
        response = JsonResponse(cached, safe=False)
        response["X-Cache-Hit"] = "1"
        return response

    productos = _helper.listar_todos().filter(estado="activo")
    if categoria_id:
        productos = productos.filter(id_cate_id=categoria_id)
    if menu_id:
        productos = productos.filter(id_menu_id=menu_id)
    if solo_destacados:
        productos = productos[:6]

    data = [_helper.producto_to_dict(producto) for producto in productos]
    cache.set(cache_key, data, timeout=300)
    response = JsonResponse(data, safe=False)
    response["X-Cache-Hit"] = "0"
    return response
