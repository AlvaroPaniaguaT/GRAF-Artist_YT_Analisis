from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class GraphItem(models.Model):
    artist_name = models.CharField(max_length=200, default=None)
    feat_artist_name = models.CharField(max_length=200, default=None)
    view_count = models.IntegerField(default=0)
    sub_count = models.IntegerField(default=0)
    genre = models.CharField(max_length=200, null=True, default='Other')
    num_feats = models.IntegerField(default=0)
    yt_channel_id = models.CharField(max_length=200, null=True)
    yt_channel_name = models.CharField(max_length=200, null=True)
    grade = models.IntegerField(default = 0, validators=[
        MaxValueValidator(10), MinValueValidator(1)
    ])

class SongsItems(models.Model):
    artist = models.CharField(max_length=200, default="Unknown artist")
    feat_artist = models.CharField(max_length=200, default="Unknown artist")
    song = models.CharField(max_length=200, default="Unknown song")
