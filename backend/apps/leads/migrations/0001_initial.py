from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('customers', '0001_initial'),
        ('organizations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('status', models.CharField(choices=[('new', 'New'), ('contacted', 'Contacted'), ('qualified', 'Qualified'), ('proposal', 'Proposal'), ('won', 'Won'), ('lost', 'Lost')], default='new', max_length=20)),
                ('source', models.CharField(blank=True, max_length=50)),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_leads', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leads', to='customers.customer')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leads', to='organizations.organization')),
            ],
            options={'ordering': ['-updated_at']},
        ),
    ]
