import csv
import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для загрузки ингредиентов из CSV или JSON файла."""

    help = 'Загрузка ингредиентов из CSV или JSON файла'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['csv', 'json'],
            default='csv',
            help='Формат файла: csv или json',
        )
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            help='Путь к папке с данными (по умолчанию: /app/data)',
        )

    def handle(self, *args, **options):
        """Основная логика команды."""
        # Гибкий путь: аргумент → настройка → значение по умолчанию
        data_dir = options.get('path')
        if not data_dir:
            data_dir = getattr(settings, 'DATA_DIR', '/app/data')

        if options['format'] == 'csv':
            file_path = os.path.join(data_dir, 'ingredients.csv')
            self.load_from_csv(file_path)
        else:
            file_path = os.path.join(data_dir, 'ingredients.json')
            self.load_from_json(file_path)

    def load_from_csv(self, file_path):
        """Загрузка ингредиентов из CSV файла."""
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'Файл {file_path} не найден')
            )
            return

        ingredients_to_create = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row.get('name') or row.get('название')
                unit = row.get('measurement_unit') or row.get(
                    'единица_измерения'
                )
                if name and unit:
                    ingredients_to_create.append(
                        Ingredient(
                            name=name.strip(),
                            measurement_unit=unit.strip()
                        )
                    )

        if ingredients_to_create:
            Ingredient.objects.bulk_create(
                ingredients_to_create,
                ignore_conflicts=True,
                batch_size=1000
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Загружено {len(ingredients_to_create)} ингредиентов '
                    f'из CSV'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING('Нет данных для загрузки')
            )

    def load_from_json(self, file_path):
        """Загрузка ингредиентов из JSON файла."""
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'Файл {file_path} не найден')
            )
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        ingredients_to_create = []
        for item in data:
            name = item.get('name') or item.get('название')
            unit = item.get('measurement_unit') or item.get(
                'единица_измерения'
            )
            if name and unit:
                ingredients_to_create.append(
                    Ingredient(
                        name=name.strip(),
                        measurement_unit=unit.strip()
                    )
                )

        if ingredients_to_create:
            Ingredient.objects.bulk_create(
                ingredients_to_create,
                ignore_conflicts=True,
                batch_size=1000
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Загружено {len(ingredients_to_create)} ингредиентов '
                    f'из JSON'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING('Нет данных для загрузки')
            )
