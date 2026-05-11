"""Comando para generar backups del sistema en JSON comprimido."""

# Librerias para comprimir, manejar JSON y fechas
import gzip
import json
from datetime import datetime
from pathlib import Path

# Herramientas de Django
from django.apps import apps
from django.core import serializers
from django.core.management.base import BaseCommand

# Comando personalizado de Django
class Command(BaseCommand):
    # Descripcion del comando
    help = "Genera una copia de seguridad JSON comprimida del contenido de la base de datos."

    # Argumentos que se pueden pasar por consola
    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            default="backups",
            help="Directorio donde se guardaran las copias de seguridad.",
        )
        parser.add_argument(
            "--keep",
            type=int,
            default=7,
            help="Numero maximo de backups que se conservaran en disco.",
        )

    # Funcion principal del comando
    def handle(self, *args, **options):
        # Carpeta donde se guardan los backups
        output_dir = Path(options["output_dir"]).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        # Nombre del archivo con fecha y hora
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"bongusto_backup_{timestamp}.json.gz"

        payload = []

        # Apps que no se incluyen en el backup
        excluded_apps = {"contenttypes"}

        # Recorre todos los modelos del sistema
        for model in apps.get_models():
            if model._meta.app_label in excluded_apps:
                continue

            queryset = model.objects.all()

            # Si no hay datos, se salta ese modelo
            if not queryset.exists():
                continue

            # Convierte los datos a JSON y los agrega
            payload.extend(
                json.loads(
                    serializers.serialize(
                        "json",
                        queryset,
                        use_natural_foreign_keys=True,
                        use_natural_primary_keys=True,
                    )
                )
            )

        # Guarda el archivo comprimido
        with gzip.open(output_file, "wt", encoding="utf-8") as gz_file:
            gz_file.write(json.dumps(payload, ensure_ascii=False))

        # Mantiene solo la cantidad de backups definida
        backups = sorted(output_dir.glob("bongusto_backup_*.json.gz"), reverse=True)
        keep = max(int(options["keep"]), 1)

        for old_backup in backups[keep:]:
            old_backup.unlink(missing_ok=True)

        # Mensaje final en consola
        self.stdout.write(self.style.SUCCESS(f"Backup creado en: {output_file}"))