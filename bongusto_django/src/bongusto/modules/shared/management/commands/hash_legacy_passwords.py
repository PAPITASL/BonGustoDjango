"""Comando para convertir contraseñas antiguas en texto plano a hash seguro."""

from django.core.management.base import BaseCommand

from bongusto.domain.models import Usuario
from bongusto.modules.shared.security import es_hash_django, hash_contrasena


class Command(BaseCommand):
    help = "Convierte a hash las contraseñas de usuarios que aún estén guardadas en texto plano."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Solo muestra cuántos usuarios serían migrados, sin guardar cambios.",
        )

    def handle(self, *args, **options):
        dry_run = bool(options.get("dry_run"))
        total_usuarios = 0
        ya_protegidas = 0
        vacias = 0
        migradas = 0

        usuarios = Usuario.objects.all().only("id_usuario", "correo", "clave")

        for usuario in usuarios.iterator():
            total_usuarios += 1
            clave = (usuario.clave or "").strip()

            if not clave:
                vacias += 1
                continue

            if es_hash_django(clave):
                ya_protegidas += 1
                continue

            migradas += 1
            if not dry_run:
                usuario.clave = hash_contrasena(clave)
                usuario.save(update_fields=["clave"])

        modo = "vista previa" if dry_run else "migración aplicada"
        self.stdout.write(self.style.SUCCESS(f"Proceso completado ({modo})."))
        self.stdout.write(f"Usuarios revisados: {total_usuarios}")
        self.stdout.write(f"Ya protegidas: {ya_protegidas}")
        self.stdout.write(f"Sin clave: {vacias}")
        self.stdout.write(f"Convertidas a hash: {migradas}")
