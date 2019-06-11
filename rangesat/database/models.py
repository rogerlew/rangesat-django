# This is an auto-generated Django model module created by ogrinspect.
import json

from datetime import date, timedelta
from django.db import models
import django.contrib.gis.db.models

from django.http import JsonResponse

from django.core.serializers import serialize

import numpy as np


class Location(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=50)

    @property
    def ranches(self):
        queryset = Ranch.objects.filter(location_id=self.id)
        return queryset

    def __str__(self):
        return 'Pasture(name={0.name}, description={0.description})'\
               .format(self)


class Ranch(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, default=None, null=True)
    ll = django.contrib.gis.db.models.PointField(default=None, null=True)
    ur = django.contrib.gis.db.models.PointField(default=None, null=True)

    @property
    def pastures(self):
        queryset = Pasture.objects.filter(ranch_id=self.id)
        return queryset

    @property
    def scene_dates(self):
        queryset = PastureStat.objects.filter(ranch_id=self.id)
        type_dates = set([(ps.analysis_type, ps.scene.acquisition_date) for ps in queryset])

        scene_dates = {}
        for t, d in type_dates:
            if t not in scene_dates:
                scene_dates[t] = set()
            scene_dates[t].add(d)

        for t in scene_dates:
            scene_dates[t] = sorted(list(scene_dates[t]))

        return scene_dates

    @property
    def analysis_types(self):
        queryset = PastureStat.objects.filter(ranch_id=self.id)
        types = sorted(list(set([ps.analysis_type for ps in queryset])))
        return types

    def __str__(self):
        return 'Pasture(name={0.name}, description={0.description})'\
               .format(self)


class Pasture(models.Model):
    name = models.CharField(max_length=50)
    ranch = models.ForeignKey(Ranch, on_delete=models.CASCADE, default=None, null=True)
    ownership = models.CharField(max_length=50, default=None, null=True)
    hectares = models.FloatField(default=None, null=True)
    acres = models.FloatField(default=None, null=True)
    shape_leng = models.FloatField(default=None, null=True)
    shape_area = models.FloatField(default=None, null=True)
    key = models.CharField(max_length=50)
    geom = django.contrib.gis.db.models.MultiPolygonField(srid=4326)
    centroid = django.contrib.gis.db.models.PointField(srid=4326, null=True)

    @property
    def pasturestats(self):
        queryset = PastureStat.objects.filter(pasture_id=self.id)
        return queryset

    @property
    def analysis_types(self):
        return self.ranch.analysis_types

    def __str__(self):
        return 'Pasture(name={0.name})'\
               .format(self)


class SceneMeta(models.Model):
    name = models.CharField(max_length=60)
    data_provider = models.CharField(max_length=50)
    instrument = models.CharField(max_length=50)

    SATELLITE_DESC = (
        ('8', 'Landsat-8'),
        ('7', 'Landsat-7'),
        ('6', 'Landsat-6'),
        ('5', 'Landsat-5'),
        ('4', 'Landsat-4'),
        ('3', 'Landsat-3'),
        ('2', 'Landsat-2'),
        ('1', 'Landsat-1')
    )
    satellite = models.CharField(max_length=50, choices=SATELLITE_DESC)

    wrs_system = models.IntegerField()
    wrs_path = models.IntegerField()
    wrs_row = models.IntegerField()
    acquisition_date = models.DateField()

    bbox = django.contrib.gis.db.models.PolygonField()

    def __str__(self):
        return 'SceneMeta(name={0.name})'\
               .format(self)


class PastureStat(models.Model):
    key = models.CharField(max_length=100)

    ANALYSIS_TYPE = (
        ('H', 'Herbaceous'),
        ('S', 'Shrub')
    )
    analysis_type = models.CharField(max_length=50, choices=ANALYSIS_TYPE, default='Herbaceous')

    scene = models.ForeignKey(SceneMeta, on_delete=models.CASCADE, default=None, null=True)
    pasture = models.ForeignKey(Pasture, on_delete=models.CASCADE, default=None, null=True)
    ranch = models.ForeignKey(Ranch, on_delete=models.CASCADE, default=None, null=True)
    model = models.CharField(max_length=50)
    sill = models.FloatField(null=True)
    range = models.FloatField(null=True)
    nugget = models.FloatField(null=True)
    msh = models.FloatField(null=True)
    meangpm = models.FloatField(null=True)
    sumbiogpm = models.FloatField(null=True)
    lbsperac_mean = models.FloatField(null=True)
    totalbio_sumlbs = models.FloatField(null=True)
    pixel_num = models.IntegerField(null=True)
    area_ac = models.FloatField(null=True)
    area_hc = models.FloatField(null=True)
    percentile_10 = models.FloatField(null=True)
    percentile_75 = models.FloatField(null=True)
    percentile_90 = models.FloatField(null=True)
    lbsperac_percentile_10 = models.FloatField(null=True)
    lbsperac_percentile_75 = models.FloatField(null=True)
    lbsperac_percentile_90 = models.FloatField(null=True)

    @property
    def date(self):
        if self.scene is None:
            return None

        return self.scene.acquisition_date

    @property
    def pasture__id(self):
        if self.pasture is None:
            return None

        return self.pasture.pk

    def __str__(self):
        return 'PastureStat(key={0.key})'\
               .format(self)


class RasterData(models.Model):
    ANALYSIS_TYPE = (
        ('H', 'Herbaceous'),
        ('S', 'Shrub')
    )
    analysis_type = models.CharField(max_length=50, choices=ANALYSIS_TYPE, default='Herbaceous')
    analysis_name = models.CharField(max_length=50, default=None, null=True)

    name = models.CharField(max_length=100, default=None, null=True)
    scene = models.ForeignKey(SceneMeta, on_delete=models.CASCADE, default=None, null=True)
    ranch = models.ForeignKey(Ranch, on_delete=models.CASCADE, default=None, null=True)
    raster = models.FileField(upload_to='rasterdata')
    wgs_raster = models.FileField(upload_to='rasterdata', default=None, null=True)

    bbox = django.contrib.gis.db.models.PolygonField(default=None, null=True)

    @property
    def date(self):
        if self.scene is None:
            return None

        return self.scene.acquisition_date

    def __str__(self):
        return 'RasterData(name={0.name})'\
               .format(self)


class GridMetTimeSeries(models.Model):
    name = models.CharField(max_length=50, default='gridMET Daily Timeseries')
    data_provider = models.CharField(max_length=50, default='http://www.climatologylab.org/gridmet.html')

    pasture = models.ForeignKey(Pasture, on_delete=models.CASCADE, default=None, null=True)
    ranch = models.ForeignKey(Ranch, on_delete=models.CASCADE, default=None, null=True)

    lon = models.FloatField(null=True)
    lat = models.FloatField(null=True)
    year = models.IntegerField(null=True)

    pr = models.BinaryField(max_length=4*366, default=None, null=True)
    pr_description = models.CharField(max_length=50, default=None, null=True)
    pr_dtype = models.CharField(max_length=10, default=None, null=True)
    pr_units = models.CharField(max_length=10, default=None, null=True)

    tmmn = models.BinaryField(max_length=4*366, default=None, null=True)
    tmmn_description = models.CharField(max_length=50, default=None, null=True)
    tmmn_dtype = models.CharField(max_length=10, default=None, null=True)
    tmmn_units = models.CharField(max_length=10, default=None, null=True)

    tmmx = models.BinaryField(max_length=4*366, default=None, null=True)
    tmmx_description = models.CharField(max_length=50, default=None, null=True)
    tmmx_dtype = models.CharField(max_length=10, default=None, null=True)
    tmmx_units = models.CharField(max_length=10, default=None, null=True)

    srad = models.BinaryField(max_length=4*366, default=None, null=True)
    srad_description = models.CharField(max_length=50, default=None, null=True)
    srad_dtype = models.CharField(max_length=10, default=None, null=True)
    srad_units = models.CharField(max_length=10, default=None, null=True)

    pdsi = models.BinaryField(max_length=4*366, default=None, null=True)
    pdsi_description = models.CharField(max_length=50, default=None, null=True)
    pdsi_dtype = models.CharField(max_length=10, default=None, null=True)
    pdsi_units = models.CharField(max_length=10, default=None, null=True)

    pet = models.BinaryField(max_length=4*366, default=None, null=True)
    pet_description = models.CharField(max_length=50, default=None, null=True)
    pet_dtype = models.CharField(max_length=10, default=None, null=True)
    pet_units = models.CharField(max_length=10, default=None, null=True)

    bi = models.BinaryField(max_length=4*366, default=None, null=True)
    bi_description = models.CharField(max_length=50, default=None, null=True)
    bi_dtype = models.CharField(max_length=10, default=None, null=True)
    bi_units = models.CharField(max_length=10, default=None, null=True)

    @property
    def pr_ts(self):
        return np.fromstring(self.pr.tobytes(), dtype=self.pr_dtype)

    @property
    def pr_cumulative_ts(self):
        x = np.fromstring(self.pr.tobytes(), dtype=self.pr_dtype)
        return np.cumsum(x)

    @property
    def pr_cumulative_ts__in(self):
        x = np.fromstring(self.pr.tobytes(), dtype=self.pr_dtype)
        return np.cumsum(x) / 25.4

    @property
    def tmmn_ts(self):
        return np.fromstring(self.tmmn.tobytes(), dtype=self.tmmn_dtype)

    @property
    def tmmx_ts(self):
        return np.fromstring(self.tmmx.tobytes(), dtype=self.tmmx_dtype)

    @property
    def srad_ts(self):
        return np.fromstring(self.srad.tobytes(), dtype=self.srad_dtype)

    @property
    def pdsi_ts(self):
        return np.fromstring(self.pdsi.tobytes(), dtype=self.pdsi_dtype)

    @property
    def pet_ts(self):
        return np.fromstring(self.pet.tobytes(), dtype=self.pet_dtype)

    @property
    def bi_ts(self):
        return np.fromstring(self.bi.tobytes(), dtype=self.bi_dtype)

    @property
    def dates(self):
        return [date(self.year, 1, 1) + timedelta(i) for i, _ in enumerate(self.pr_ts)]

