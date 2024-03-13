import csv
import os

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
                    for field in model._meta.fields:
                        if isinstance(field, models.ForeignKey) or isinstance(field, models.ManyToManyField):
                            id_field_name = field.name + '_id'
                            if id_field_name in row:
                                try:
                                    id_value = row.pop(id_field_name)
                                    related_model = field.remote_field.model
                                    related_instance = related_model.objects.get(pk=id_value)
                                    row[field.name] = related_instance
                                except (KeyError, related_model.DoesNotExist) as e:
                                    self.stdout.write(f'Error processing {field.name} id: {e}')
                                    continue
                    # for field in row:
                    #     print(hasattr(model, field+'id'), field)
                    #     # model_fields = [field.name for field in model._meta.get_fields()]
                    #     # print(*[(hasattr(model, field), field) for field in row])
                    #     # print(hasattr(model, field), field)
                    #     # obj = model(**row)
                    #     # obj.save()
                    # break
                self.stdout.write(f'Данные из модели {model} успешно импортированы')
        except FileNotFoundError as error:
            self.stdout.write(f'Файл с указанным названием {filename} не найден')
