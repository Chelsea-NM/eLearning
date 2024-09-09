# Generated by Django 5.1 on 2024-09-07 12:53

import django.db.models.deletion
import eLearning_api.utils
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eLearning_api', '0012_usercourse_user_alter_usercourse_created_by'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseFeedback',
            fields=[
                ('course_feedback_id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('created_by_username', models.CharField(blank=True, max_length=255)),
                ('status', models.IntegerField(choices=[(0, 'undefined'), (10, 'Active'), (40, 'Blocked'), (50, 'Archived')], default=eLearning_api.utils.Status['Active'])),
                ('message', models.CharField(blank=True, max_length=255)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eLearning_api.course')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
