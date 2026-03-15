# Generated manually to delete PoemCategory model

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_alter_poem_category'),
    ]

    operations = [
        # Delete the PoemCategory table
        migrations.DeleteModel(
            name='PoemCategory',
        ),
    ]