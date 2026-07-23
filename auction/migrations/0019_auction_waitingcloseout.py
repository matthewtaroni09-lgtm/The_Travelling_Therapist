from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0018_alter_raffle_image_help_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='waitingCloseout',
            field=models.BooleanField(default=False, verbose_name='Closed Waiting Listing'),
        ),
    ]
