# Generated by Django 5.1 on 2024-09-05 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eLearning_api', '0005_course_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='modified_date',
            field=models.DateTimeField(null=True),
        ),
    ]
