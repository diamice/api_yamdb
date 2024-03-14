import csv
import os
from django.db import models
from django.db.models.fields.related import ForeignKey, ManyToManyField

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
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
                        # print([fields.name for fields in model._meta.fields if type(fields) == ForeignKey or type(fields) == ManyToManyField])
                        # print(field)
                        if hasattr(row_obj, field + '_id'):
                            setattr(row_obj, field + '_id', row.get(field))
                        else:
                            setattr(row_obj, field, row.get(field))
                        # print(hasattr(model, field + '_id'), field, isinstance(field + '_id', ForeignKey))
                        # model_fields = [field.name for field in model._meta.get_fields()]
                        # print(*[(hasattr(model, field), field) for field in row])
                        # print(hasattr(model, field), field)
                    print(row_obj)
                    row_obj.save()
                self.stdout.write(f'Данные из модели {model} успешно импортированы')
        except FileNotFoundError as error:
            self.stdout.write(f'Файл с указанным названием {filename} не найден')
