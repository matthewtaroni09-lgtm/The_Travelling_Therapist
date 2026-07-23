from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0017_alter_flat_fee_guidance_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='raffle',
            name='image',
            field=models.ImageField(blank=True, help_text='Upload an image less than 5MB. If not provided, the Material Icon will be used.', null=True, upload_to='raffle_images/'),
        ),
    ]
