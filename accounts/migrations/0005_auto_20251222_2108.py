from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_rename_pdf_url_book_content_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='content_url',
            new_name='pdf_url',
        ),
    ]
