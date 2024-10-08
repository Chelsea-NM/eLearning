# Generated by Django 5.1 on 2024-09-05 23:13

import eLearning_api.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eLearning_api', '0006_alter_course_modified_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coursematerial',
            name='filename',
        ),
        migrations.AddField(
            model_name='coursematerial',
            name='file_name',
            field=models.ImageField(blank=True, upload_to='images/course/material/'),
        ),
        migrations.AlterField(
            model_name='coursematerial',
            name='type',
            field=models.IntegerField(choices=[(0, 'Generic'), (10, 'Image'), (20, 'Pdf'), (30, 'Word'), (40, 'Excel'), (50, 'Csv')], default=eLearning_api.utils.CourseMaterialType['Generic']),
        ),
        migrations.AlterField(
            model_name='userstatus',
            name='media_image',
            field=models.ImageField(blank=True, upload_to='images/posts/'),
        ),
    ]
