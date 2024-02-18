# Generated by Django 4.2.10 on 2024-02-18 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elearn_app', '0003_course_module_code_material_title_alter_material_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='status',
            field=models.CharField(blank=True, default='', max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='module_code',
            field=models.CharField(max_length=256, unique=True),
        ),
    ]