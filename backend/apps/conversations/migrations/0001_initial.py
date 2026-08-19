from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('channels', '0001_initial'),
        ('customers', '0001_initial'),
        ('organizations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('open', 'Open'), ('pending', 'Pending'), ('closed', 'Closed')], default='open', max_length=20)),
                ('unread_count', models.PositiveIntegerField(default=0)),
                ('last_message_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='conversations', to=settings.AUTH_USER_MODEL)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversations', to='channels.channel')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversations', to='customers.customer')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversations', to='organizations.organization')),
            ],
            options={'ordering': ['-last_message_at', '-updated_at']},
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=255)),
                ('direction', models.CharField(choices=[('inbound', 'Inbound'), ('outbound', 'Outbound'), ('internal', 'Internal')], max_length=20)),
                ('message_type', models.CharField(choices=[('text', 'Text'), ('image', 'Image'), ('video', 'Video'), ('file', 'File'), ('audio', 'Audio'), ('system', 'System')], default='text', max_length=20)),
                ('content', models.TextField(blank=True)),
                ('attachment_url', models.URLField(blank=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='conversations.conversation')),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['created_at'], 'indexes': [models.Index(fields=['conversation', 'created_at'], name='conversations_m_convers_fa5f5e_idx'), models.Index(fields=['external_id'], name='conversations_m_externa_b4cd4e_idx')]},
        ),
    ]
