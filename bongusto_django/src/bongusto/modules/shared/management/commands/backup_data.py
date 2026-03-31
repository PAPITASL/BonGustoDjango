"""Comando para generar copias de seguridad JSON comprimidas del sistema."""

import gzip
import json
from datetime import datetime
from pathlib import Path

from django.apps import apps
from django.core import serializers
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Genera una copia de seguridad JSON comprimida del contenido de la base de datos."

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

    def handle(self, *args, **options):
        output_dir = Path(options["output_dir"]).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"bongusto_backup_{timestamp}.json.gz"

        payload = []
        excluded_apps = {"contenttypes"}

        for model in apps.get_models():
            if model._meta.app_label in excluded_apps:
                continue
            queryset = model.objects.all()
            if not queryset.exists():
                continue
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

        with gzip.open(output_file, "wt", encoding="utf-8") as gz_file:
            gz_file.write(json.dumps(payload, ensure_ascii=False))

        backups = sorted(output_dir.glob("bongusto_backup_*.json.gz"), reverse=True)
        keep = max(int(options["keep"]), 1)
        for old_backup in backups[keep:]:
            old_backup.unlink(missing_ok=True)

        self.stdout.write(self.style.SUCCESS(f"Backup creado en: {output_file}"))
