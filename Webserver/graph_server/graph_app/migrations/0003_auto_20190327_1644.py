# Generated by Django 2.1.7 on 2019-03-27 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graph_app', '0002_auto_20190327_1633'),
    ]

    operations = [
        migrations.AddField(
            model_name='graphitem',
            name='genre',
            field=models.CharField(default=None, max_length=200),
        ),
        migrations.AddField(
            model_name='graphitem',
            name='grade',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='graphitem',
            name='song',
            field=models.CharField(default=None, max_length=200),
        ),
        migrations.AddField(
            model_name='graphitem',
            name='yt_channel_id',
            field=models.CharField(default=None, max_length=200),
        ),
        migrations.AddField(
            model_name='graphitem',
            name='yt_channel_name',
            field=models.CharField(default=None, max_length=200),
        ),
        migrations.AlterField(
            model_name='graphitem',
            name='artist_name',
            field=models.CharField(default=None, max_length=200),
        ),
        migrations.AlterField(
            model_name='graphitem',
            name='feat_artist_name',
            field=models.CharField(default=None, max_length=200),
        ),
    ]
