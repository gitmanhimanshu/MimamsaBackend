# Generated manually to change Poem category from ForeignKey to CharField

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_poem_genre'),
    ]

    operations = [
        # First, set all existing poem categories to null to avoid conflicts
        migrations.RunSQL(
            "UPDATE accounts_poem SET category_id = NULL WHERE category_id IS NOT NULL;",
            reverse_sql="",
        ),
        
        # Remove the foreign key constraint
        migrations.RemoveField(
            model_name='poem',
            name='category',
        ),
        
        # Add the new CharField category
        migrations.AddField(
            model_name='poem',
            name='category',
            field=models.CharField(blank=True, choices=[('love', 'प्रेम कविता'), ('nature', 'प्रकृति'), ('patriotic', 'देशभक्ति'), ('spiritual', 'आध्यात्मिक'), ('social', 'सामाजिक'), ('motivational', 'प्रेरणादायक'), ('sad', 'दुःख'), ('funny', 'हास्य')], max_length=50, null=True),
        ),
    ]