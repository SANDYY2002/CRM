from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [('organizations', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('facebook', 'Facebook'), ('instagram', 'Instagram'), ('whatsapp', 'WhatsApp'), ('viber', 'Viber'), ('youtube', 'YouTube'), ('website', 'Website'), ('email', 'Email')], max_length=30)),
                ('name', models.CharField(max_length=150)),
                ('external_id', models.CharField(blank=True, max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('credentials', models.JSONField(blank=True, default=dict)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channels', to='organizations.organization')),
            ],
            options={'constraints': [models.UniqueConstraint(fields=('organization', 'type', 'external_id'), name='unique_channel_external_id')]},
        ),
    ]
