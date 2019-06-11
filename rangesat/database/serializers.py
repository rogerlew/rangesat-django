from rest_framework.serializers import HyperlinkedModelSerializer

from .models import (
    Pasture,
    Ranch,
    Location,
    PastureStat,
    SceneMeta,
    RasterData,
    GridMetTimeSeries
)


class PastureStatSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = PastureStat
        fields = ('id', 'key', 'analysis_type', 'scene', 'date',
                  'pasture', 'pasture__id', 'ranch', 'model', 'sill', 'range',
                  'nugget', 'msh', 'meangpm', 'sumbiogpm', 'lbsperac_mean',
                  'totalbio_sumlbs', 'pixel_num', 'area_ac', 'area_hc',
                  'percentile_10', 'percentile_75', 'percentile_90',
                  'lbsperac_percentile_10', 'lbsperac_percentile_75', 'lbsperac_percentile_90')


class PastureSerializer(HyperlinkedModelSerializer):
    pasturestats = PastureStatSerializer(many=True)

    class Meta:
        model = Pasture
        fields = ('id', 'url', 'name', 'ranch', 'ownership', 'hectares', 'acres',
                  'shape_leng', 'shape_area', 'key', 'geom', 'centroid', 'pasturestats')


class RanchSerializer(HyperlinkedModelSerializer):
    pastures = PastureSerializer(many=True)

    class Meta:
        model = Ranch
        fields = ('id', 'url', 'name', 'description', 'll', 'ur',
                  'location', 'pastures', 'scene_dates', 'analysis_types')


class LocationSerializer(HyperlinkedModelSerializer):
    ranches = RanchSerializer(many=True)

    class Meta:
        model = Location
        fields = ('id', 'url', 'name', 'description', 'ranches')


class SceneMetaSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = SceneMeta
        fields = ('id', 'name', 'data_provider', 'instrument', 'satellite',
                  'wrs_system', 'wrs_path', 'wrs_row',
                  'acquisition_date', 'bbox')


class RasterDataSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = RasterData
        fields = ('id', 'name', 'analysis_name', 'analysis_type', 'scene', 'ranch',
                  'wgs_raster', 'raster', 'bbox')


class GridMetTimeSeriesSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = GridMetTimeSeries
        fields = ('id', 'name', 'data_provider', 'pasture', 'ranch',
                  'lon', 'lat', 'year',
                  'pr', 'pr_description', 'pr_dtype', 'pr_units',
                  'tmmn', 'tmmn_description', 'tmmn_dtype', 'tmmn_units',
                  'tmmx', 'tmmx_description', 'tmmx_dtype', 'tmmx_units',
                  'srad', 'srad_description', 'srad_dtype', 'srad_units',
                  'pdsi', 'pdsi_description', 'pdsi_dtype', 'pdsi_units',
                  'pet', 'pet_description', 'pet_dtype', 'pet_units',
                  'bi', 'bi_description', 'bi_dtype', 'bi_units')
