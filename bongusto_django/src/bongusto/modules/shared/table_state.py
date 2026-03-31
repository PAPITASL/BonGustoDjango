"""Estado simulado de cinco mesas compartidas entre clientes y meseros."""

from django.core.cache import cache
from django.utils import timezone


MESA_CACHE_KEY = "bongusto.simulacion.mesas"


class MesaStateService:
    """Administra una simulacion simple de cinco mesas."""

    def _mesa_base(self, mesa_id):
        return {
            "id": mesa_id,
            "estado": "disponible",
            "id_usuario": None,
            "cliente_nombre": "",
            "cliente_correo": "",
            "asignado_en": None,
        }

    def _estado_inicial(self):
        return [self._mesa_base(mesa_id) for mesa_id in range(1, 6)]

    def listar(self):
        mesas = cache.get(MESA_CACHE_KEY)
        if isinstance(mesas, list) and len(mesas) == 5:
            return mesas

        mesas = self._estado_inicial()
        cache.set(MESA_CACHE_KEY, mesas, timeout=None)
        return mesas

    def guardar(self, mesas):
        cache.set(MESA_CACHE_KEY, mesas, timeout=None)
        return mesas

    def mesa_por_usuario(self, usuario_id):
        if not usuario_id:
            return None

        for mesa in self.listar():
            if mesa.get("id_usuario") == usuario_id:
                return mesa
        return None

    def asignar_a_usuario(self, usuario):
        actual = self.mesa_por_usuario(usuario.id_usuario)
        if actual:
            return actual

        mesas = self.listar()
        disponible = next(
            (mesa for mesa in mesas if (mesa.get("estado") or "").lower() == "disponible"),
            None,
        )
        if not disponible:
            return None

        # Cuando una mesa se asigna a un cliente deja de estar libre.
        # En la app de meseros este estado se representa en rojo como ocupada.
        disponible["estado"] = "con_pedidos"
        disponible["id_usuario"] = usuario.id_usuario
        disponible["cliente_nombre"] = usuario.nombre_completo() or usuario.correo or f"Cliente {usuario.id_usuario}"
        disponible["cliente_correo"] = usuario.correo or ""
        disponible["asignado_en"] = timezone.now().isoformat()
        self.guardar(mesas)
        return disponible

    def actualizar_estado(self, mesa_id, estado):
        estado_normalizado = (estado or "").strip().lower()
        if estado_normalizado not in {"disponible", "pagada", "con_pedidos"}:
            return None

        mesas = self.listar()
        mesa = next((item for item in mesas if item.get("id") == mesa_id), None)
        if not mesa:
            return None

        if estado_normalizado == "disponible":
            mesa.update(self._mesa_base(mesa_id))
        else:
            mesa["estado"] = estado_normalizado

        self.guardar(mesas)
        return mesa

    def liberar(self, mesa_id):
        mesas = self.listar()
        mesa = next((item for item in mesas if item.get("id") == mesa_id), None)
        if not mesa:
            return None

        mesa.update(self._mesa_base(mesa_id))
        self.guardar(mesas)
        return mesa


__all__ = ["MesaStateService", "MESA_CACHE_KEY"]
