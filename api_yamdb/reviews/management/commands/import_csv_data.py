import csv
import os

from django.core.management.base import BaseCommand
from django.apps import apps

from api_yamdb.settings import BASE_DIR

FILES_PATH = BASE_DIR / 'static' / 'data'


class Command(BaseCommand):
    """Help import csv data into project database."""
    help = 'Help import csv data into project database'

    def add_arguments(self, parser):
        parser.add_argument('model', help='Имя модели для импорта данных')
        parser.add_argument('filename', help='Имя файла')

    def handle(self, *args, **options):
        model = apps.get_model('reviews', options['model'])
        filename = options['filename'] + '.csv'
        path_to_selected_file = os.path.join(FILES_PATH, filename)
        try:
            with open(path_to_selected_file, encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    row_obj = model()
                    for field in row:
                        if hasattr(row_obj, field + '_id'):
                            setattr(row_obj, field + '_id', row.get(field))
                        else:
                            setattr(row_obj, field, row.get(field))
                    row_obj.save()
                self.stdout.write(f'Данные для модели {model} '
                                  f'успешно импортированы')
        except FileNotFoundError:
            self.stdout.write(f'Файл с указанным названием {filename}'
                              f' не найден')
