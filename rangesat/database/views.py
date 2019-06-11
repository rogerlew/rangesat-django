import json

from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from django.core.serializers import serialize
from django.http import JsonResponse

import numpy as np

from .models import (
    Pasture,
    Ranch,
    Location,
    PastureStat,
    SceneMeta,
    RasterData,
    GridMetTimeSeries
)
from .serializers import (
    PastureSerializer,
    RanchSerializer,
    LocationSerializer,
    PastureStatSerializer,
    SceneMetaSerializer,
    RasterDataSerializer,
    GridMetTimeSeriesSerializer
)


class PastureView(ModelViewSet):
    queryset = Pasture.objects.all()
    serializer_class = PastureSerializer


class RanchView(ModelViewSet):
    queryset = Ranch.objects.all()
    serializer_class = RanchSerializer


class LocationView(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class PastureStatView(ModelViewSet):
    queryset = PastureStat.objects.all()
    serializer_class = PastureStatSerializer

    def get_queryset(self):
        queryset = self.queryset

        analysis_type = self.request.query_params.get('analysis_type', None)
        if analysis_type is not None:
            queryset = queryset.filter(analysis_type=analysis_type)

        ranch = self.request.query_params.get('ranch', None)
        if ranch is not None:
            queryset = queryset.filter(ranch__name=ranch)

        acquisition_date = self.request.query_params.get('acquisition_date', None)
        if acquisition_date is not None:
            queryset = queryset.filter(scene__acquisition_date=acquisition_date)

        return queryset


class SceneMetaView(ModelViewSet):
    queryset = SceneMeta.objects.all()
    serializer_class = SceneMetaSerializer


class RasterDataView(ModelViewSet):
    queryset = RasterData.objects.all()
    serializer_class = RasterDataSerializer

    def get_queryset(self):
        queryset = self.queryset

        analysis_type = self.request.query_params.get('analysis_type', None)
        if analysis_type is not None:
            queryset = queryset.filter(analysis_type=analysis_type)

        analysis_name = self.request.query_params.get('analysis_name', None)
        if analysis_name is not None:
            queryset = queryset.filter(analysis_name=analysis_name)

        ranch = self.request.query_params.get('ranch', None)
        if ranch is not None:
            queryset = queryset.filter(ranch__name=ranch)

        acquisition_date = self.request.query_params.get('acquisition_date', None)
        if acquisition_date is not None:
            queryset = queryset.filter(scene__acquisition_date=acquisition_date)

        return queryset


class GridMetTimeSeriesView(ModelViewSet):
    queryset = GridMetTimeSeries.objects.all()
    serializer_class = GridMetTimeSeriesSerializer


def geojson_ranchpastures_view_filter(request, ranch=None):
    if ranch is None:
        return JsonResponse(
            json.loads(
                serialize('geojson', Pasture.objects.all(),
                          geometry_field='geom',
                          fields=('name', 'pk', 'centroid'))))

    else:
        return JsonResponse(
            json.loads(
                serialize('geojson',
                          Pasture.objects.filter(ranch__name__contains=ranch),
                          geometry_field='geom',
                          fields=('name', 'pk', 'centroid'))))


def json_pr_view_filter(request, pasture):
    queryset = GridMetTimeSeries.objects.filter(pasture__pk=pasture)
    pr_s = [np.fromstring(gmts.pr.tobytes(), dtype=gmts.pr_dtype) for gmts in queryset]
    pr_s = [pr[:365] for pr in pr_s]
    pr_s = np.concatenate([x[:, None] for x in pr_s if len(x) == 365], axis=1)

    average = np.average(pr_s, axis=1)
    median = np.average(pr_s, axis=1)
    pctl_10 = np.percentile(pr_s, 10, axis=1)

    pctl_90 = np.percentile(pr_s, 90, axis=1)
    return JsonResponse({'average': average.tolist(),
                         'median': median.tolist(),
                         'pctl_10': pctl_10.tolist(),
                         'pctl_90': pctl_90.tolist()})

