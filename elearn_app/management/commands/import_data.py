from django.core.management.base import BaseCommand, CommandError
from elearn_app.data import import_scripts 

class Command(BaseCommand):
    help = 'Imports data from CSV files into the database'

    def handle(self, *args, **options):
        try:
            import_scripts.import_user('elearn_app/data/rawdata/CM3035 Final Assignment Data - User.csv')
            import_scripts.import_userProfile('elearn_app/data/rawdata/CM3035 Final Assignment Data - UserProfile.csv')
            import_scripts.import_course('elearn_app/data/rawdata/CM3035 Final Assignment Data - Course.csv')
            import_scripts.import_assignment('elearn_app/data/rawdata/CM3035 Final Assignment Data - Assignment.csv')
            import_scripts.import_material('elearn_app/data/rawdata/CM3035 Final Assignment Data - Material.csv')
            import_scripts.import_feedback('elearn_app/data/rawdata/CM3035 Final Assignment Data - Feedback.csv')
            self.stdout.write(self.style.SUCCESS('Data import completed successfully.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR('Data import failed.'))
            raise CommandError(f'Error during import: {e}')

