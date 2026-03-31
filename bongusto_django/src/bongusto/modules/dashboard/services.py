"""Servicios sencillos del dashboard para mostrar resumenes del sistema."""

import calendar
from datetime import date

from django.db.models import Count

from bongusto.domain.models import Categoria, Menu, Musica, Producto, Reserva, Usuario


class DashboardService:
    """Servicio principal del dashboard.

    La idea de esta clase es mantener la logica dividida en pasos pequenos
    para que sea facil seguirla por alguien que esta empezando con Django.
    """

    COLOR_PRINCIPAL = "#b85c74"
    PALETA_METRICAS = [
        {"inicio": "#e7b5c4", "fin": "#d99bb0"},
        {"inicio": "#f5d7a8", "fin": "#eec98b"},
        {"inicio": "#b8dced", "fin": "#9fcfe5"},
        {"inicio": "#bfe3d0", "fin": "#a8d6c0"},
    ]
    PALETA_BARRAS = ["#d8a7b8", "#ebc791", "#a8cfdf", "#c7b9e8", "#abd7c0"]
    PALETA_USUARIOS = ["#d9a8b7", "#e7c799", "#a7d3d4", "#c7b6e6", "#b6d9b7"]
    PALETA_OPERATIVA = ["#d9b1bd", "#ecc9aa", "#b5d4e8", "#c9c1e8", "#b8dcc8"]

    def obtener_estadisticas(self):
        """Devuelve totales y estructuras visuales del dashboard."""
        totales = self._obtener_totales()
        datos_visuales = self._obtener_datos_visuales(totales)
        totales.update(datos_visuales)
        return totales

    def obtener_ultimos(self):
        """Devuelve los ultimos registros de los modulos principales."""
        ultimos_menus = Menu.objects.all()[:5]
        ultimos_productos = Producto.objects.select_related("id_menu", "id_cate").all()[:5]
        ultimas_musicas = Musica.objects.all()[:5]
        ultimas_reservas = Reserva.objects.select_related("id_usuario").all()[:5]

        return {
            "ultimos_menus": ultimos_menus,
            "ultimos_productos": ultimos_productos,
            "ultimas_musicas": ultimas_musicas,
            "ultimas_reservas": ultimas_reservas,
            "ultimos_registros": self._armar_bloques_ultimos(
                ultimos_menus=ultimos_menus,
                ultimos_productos=ultimos_productos,
                ultimas_musicas=ultimas_musicas,
                ultimas_reservas=ultimas_reservas,
            ),
        }

    def _obtener_totales(self):
        """Cuenta los registros principales del panel."""
        return {
            "total_usuarios": Usuario.objects.count(),
            "total_menus": Menu.objects.count(),
            "total_productos": Producto.objects.count(),
            "total_categorias": Categoria.objects.count(),
            "total_musica": Musica.objects.count(),
            "total_reservas": Reserva.objects.count(),
        }

    def _obtener_datos_visuales(self, totales):
        """Arma las listas que usa la vista para pintar tarjetas y graficas."""
        metricas_resumen = self._crear_metricas_resumen(totales)
        actividad_modulos = self._crear_actividad_modulos(totales)
        usuarios_por_tipo = self._crear_usuarios_por_tipo()
        resumen_operativo = self._crear_resumen_operativo(totales)
        resumen_general = self._crear_resumen_general(totales)

        return {
            "metricas_resumen": metricas_resumen,
            "actividad_modulos": actividad_modulos,
            "usuarios_por_tipo": usuarios_por_tipo,
            "resumen_operativo": resumen_operativo,
            "resumen_general_total": resumen_general["total"],
            "resumen_general_porcentaje": resumen_general["porcentaje"],
            "lineas_reserva": self._obtener_linea_reservas(),
            "calendario_dashboard": self._obtener_calendario_actual(),
        }

    def _crear_metricas_resumen(self, totales):
        """Crea las tarjetas redondas superiores."""
        datos_base = [
            ("Usuarios", totales["total_usuarios"], "fa-users"),
            ("Menus", totales["total_menus"], "fa-list"),
            ("Productos", totales["total_productos"], "fa-box-open"),
            ("Categorias", totales["total_categorias"], "fa-tags"),
        ]

        valor_maximo = 1
        for _, valor, _ in datos_base:
            if valor > valor_maximo:
                valor_maximo = valor

        metricas = []
        for indice, (titulo, valor, icono) in enumerate(datos_base):
            porcentaje = self._calcular_porcentaje(valor, valor_maximo)
            if valor > 0 and porcentaje < 8:
                porcentaje = 8

            paleta = self.PALETA_METRICAS[indice % len(self.PALETA_METRICAS)]

            metricas.append(
                {
                    "titulo": titulo,
                    "valor": valor,
                    "icono": icono,
                    "porcentaje": porcentaje,
                    "color_inicio": paleta["inicio"],
                    "color_fin": paleta["fin"],
                }
            )

        return metricas

    def _crear_actividad_modulos(self, totales):
        """Crea las barras de actividad por modulo."""
        actividad = [
            self._crear_item_actividad("Usuarios", totales["total_usuarios"], 0),
            self._crear_item_actividad("Menus", totales["total_menus"], 1),
            self._crear_item_actividad("Productos", totales["total_productos"], 2),
            self._crear_item_actividad("Musica", totales["total_musica"], 3),
            self._crear_item_actividad("Reservas", totales["total_reservas"], 4),
        ]

        valor_maximo = 1
        for item in actividad:
            if item["valor"] > valor_maximo:
                valor_maximo = item["valor"]

        for item in actividad:
            item["porcentaje"] = self._calcular_porcentaje(item["valor"], valor_maximo)

        return actividad

    def _crear_item_actividad(self, nombre, valor, indice):
        """Devuelve un item simple para una barra del dashboard."""
        return {
            "nombre": nombre,
            "valor": valor,
            "color": self.PALETA_BARRAS[indice % len(self.PALETA_BARRAS)],
            "porcentaje": 0,
        }

    def _crear_usuarios_por_tipo(self):
        """Cuenta usuarios agrupados por su tipo."""
        consulta = (
            Usuario.objects.exclude(tipo_usuario__isnull=True)
            .exclude(tipo_usuario="")
            .values("tipo_usuario")
            .annotate(total=Count("id_usuario"))
            .order_by("-total")[:5]
        )

        total_general = 0
        for item in consulta:
            total_general += item["total"]

        if total_general == 0:
            total_general = 1

        usuarios = []
        for indice, item in enumerate(consulta):
            usuarios.append(
                {
                    "label": (item["tipo_usuario"] or "sin tipo").capitalize(),
                    "total": item["total"],
                    "porcentaje": self._calcular_porcentaje(item["total"], total_general),
                    "color": self.PALETA_USUARIOS[indice % len(self.PALETA_USUARIOS)],
                }
            )

        return usuarios

    def _crear_resumen_operativo(self, totales):
        """Crea los indicadores de pulso operativo."""
        resumen = [
            self._crear_indicador(
                "Usuarios activos",
                Usuario.objects.filter(estado__iexact="Activo").count(),
                0,
            ),
            self._crear_indicador(
                "Usuarios inactivos",
                Usuario.objects.filter(estado__iexact="Inactivo").count(),
                1,
            ),
            self._crear_indicador(
                "Reservas activas",
                Reserva.objects.filter(estado_reser__iexact="activa").count(),
                2,
            ),
            self._crear_indicador(
                "Reservas canceladas",
                Reserva.objects.filter(estado_reser__iexact="cancelada").count(),
                3,
            ),
            self._crear_indicador(
                "Catalogo total",
                totales["total_menus"] + totales["total_productos"] + totales["total_musica"],
                4,
            ),
        ]

        valor_maximo = 1
        for item in resumen:
            if item["value"] > valor_maximo:
                valor_maximo = item["value"]

        for item in resumen:
            item["porcentaje"] = self._calcular_porcentaje(item["value"], valor_maximo)

        return resumen

    def _crear_indicador(self, etiqueta, valor, indice):
        """Devuelve un indicador simple para el pulso del sistema."""
        return {
            "label": etiqueta,
            "value": valor,
            "accent": self.PALETA_OPERATIVA[indice % len(self.PALETA_OPERATIVA)],
            "porcentaje": 0,
        }

    def _crear_resumen_general(self, totales):
        """Calcula el porcentaje principal del bloque resumen."""
        total_principal = (
            totales["total_usuarios"]
            + totales["total_reservas"]
            + totales["total_productos"]
        )

        porcentaje = self._calcular_porcentaje(
            totales["total_usuarios"],
            total_principal,
        )

        return {"total": total_principal, "porcentaje": porcentaje}

    def _obtener_linea_reservas(self):
        """Crea los puntos de la grafica de reservas por mes."""
        meses = self._obtener_ultimos_seis_meses()
        puntos = []

        for year, month in meses:
            total = Reserva.objects.filter(
                fecha_reser__year=year,
                fecha_reser__month=month,
            ).count()
            puntos.append(
                {
                    "label": calendar.month_abbr[month],
                    "value": total,
                }
            )

        valor_maximo = 1
        for punto in puntos:
            if punto["value"] > valor_maximo:
                valor_maximo = punto["value"]

        cantidad_puntos = len(puntos)
        if cantidad_puntos <= 1:
            paso_x = 100
        else:
            paso_x = 100 / (cantidad_puntos - 1)

        polyline = []
        area = ["0,100"]

        for indice, punto in enumerate(puntos):
            x = round(indice * paso_x, 2)
            altura = 0
            if valor_maximo > 0:
                altura = (punto["value"] / valor_maximo) * 78
            y = round(100 - altura, 2)

            punto["x"] = x
            punto["y"] = y

            polyline.append(f"{x},{y}")
            area.append(f"{x},{y}")

        area.append("100,100")

        return {
            "points": puntos,
            "polyline": " ".join(polyline),
            "area": " ".join(area),
            "max_value": valor_maximo,
        }

    def _obtener_ultimos_seis_meses(self):
        """Devuelve una lista con los ultimos seis meses incluyendo el actual."""
        hoy = date.today()
        meses = []

        for offset in range(5, -1, -1):
            year = hoy.year
            month = hoy.month - offset

            while month <= 0:
                month += 12
                year -= 1

            meses.append((year, month))

        return meses

    def _obtener_calendario_actual(self):
        """Devuelve la estructura del calendario del mes actual."""
        hoy = date.today()
        return {
            "month_name": calendar.month_name[hoy.month],
            "year": hoy.year,
            "weekdays": ["D", "L", "M", "M", "J", "V", "S"],
            "weeks": calendar.Calendar(firstweekday=6).monthdayscalendar(
                hoy.year,
                hoy.month,
            ),
            "today": hoy.day,
        }

    def _armar_bloques_ultimos(
        self,
        ultimos_menus,
        ultimos_productos,
        ultimas_musicas,
        ultimas_reservas,
    ):
        """Convierte los ultimos registros en bloques faciles de recorrer en HTML."""
        return [
            {
                "titulo": "Ultimos menus",
                "items": [menu.nombre_menu or "Sin nombre" for menu in ultimos_menus],
            },
            {
                "titulo": "Ultimos productos",
                "items": [
                    producto.nombre_producto or "Sin nombre"
                    for producto in ultimos_productos
                ],
            },
            {
                "titulo": "Ultimas musicas",
                "items": [musica.nombre_musica or "Sin nombre" for musica in ultimas_musicas],
            },
            {
                "titulo": "Ultimas reservas",
                "items": [
                    f"Reserva {reserva.id_reser} - {reserva.estado_reser or 'Sin estado'}"
                    for reserva in ultimas_reservas
                ],
            },
        ]

    def _calcular_porcentaje(self, valor, total):
        """Calcula un porcentaje entero de forma segura."""
        if total <= 0:
            return 0
        return int(round((valor / total) * 100))


__all__ = ["DashboardService"]
