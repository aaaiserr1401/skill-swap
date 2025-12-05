# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_user_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('user', 'Обычный пользователь'), ('admin', 'Администратор'), ('moderator', 'Модератор')], default='user', max_length=20),
        ),
    ]

