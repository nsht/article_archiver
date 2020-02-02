# Generated by Django 3.0.1 on 2020-02-02 18:54

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('archiver', '0008_auto_20200202_1725'),
    ]

    operations = [
        migrations.RenameField(
            model_name='articlelist',
            old_name='article_id',
            new_name='article_data',
        ),
        migrations.AlterUniqueTogether(
            name='articlelist',
            unique_together={('user', 'article_data')},
        ),
    ]