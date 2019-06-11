"""rangesat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    PastureView,
    RanchView,
    LocationView,
    PastureStatView,
    SceneMetaView,
    RasterDataView,
    GridMetTimeSeriesView,
    geojson_ranchpastures_view_filter,
    json_pr_view_filter
)

router = DefaultRouter()
router.register('pastures', PastureView)
router.register('ranches', RanchView)
router.register('locations', LocationView)
router.register('pasturestats', PastureStatView)
router.register('scenemetas', SceneMetaView)
router.register('rasterdata', RasterDataView)
router.register('gridmettimeseries', GridMetTimeSeriesView)


urlpatterns = [
    path('', include(router.urls)),
    path('geojson/', geojson_ranchpastures_view_filter),
    path('geojson/<str:ranch>/', geojson_ranchpastures_view_filter),
    path('gridmet/pr/<str:pasture>', json_pr_view_filter)
]
