from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [('organizations', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone', models.CharField(blank=True, max_length=30)),
                ('company', models.CharField(blank=True, max_length=150)),
                ('avatar_url', models.URLField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customers', to='organizations.organization')),
            ],
            options={'ordering': ['-updated_at'], 'indexes': [models.Index(fields=['organization', 'email'], name='customers_cust_org_i_a4b7c3_idx'), models.Index(fields=['organization', 'phone'], name='customers_cust_org_i_7c0e4f_idx')]},
        ),
        migrations.CreateModel(
            name='CustomerTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('color', models.CharField(default='violet', max_length=20)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_tags', to='organizations.organization')),
                ('customers', models.ManyToManyField(blank=True, related_name='tags', to='customers.customer')),
            ],
            options={'constraints': [models.UniqueConstraint(fields=('organization', 'name'), name='unique_customer_tag')]},
        ),
    ]
