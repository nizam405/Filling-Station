from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Renames a Django Project'

    def add_arguments(self, parser):
        parser.add_argument('new_project_name', type=str, help='The new Djnago project name')

    def handle(self, *args, **kwargs):
        # 
        current_project_name = 'django_project_boilerplate'
        new_project_name = kwargs['new_project_name']
        # 
        files_to_rename = [
            current_project_name + '/settings/base.py',
            current_project_name + '/wsgi.py',
            'manage.py'
        ]
        
        for f in files_to_rename:
            with open(f, 'r') as file:
                filedata = file.read()
            filedata = filedata.replace(current_project_name, new_project_name)

            with open(f, 'w') as file:
                file.write(filedata)
        os.rename(current_project_name, new_project_name)

        self.stdout.write(self.style.SUCCESS('Project has been renamed to %s' % new_project_name))