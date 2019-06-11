from django.contrib import admin
from .models import (
    Pasture,
    Ranch,
    Location,
    PastureStat,
    SceneMeta,
#    RasterData
)

admin.site.register(Pasture)
admin.site.register(Ranch)
admin.site.register(Location)
admin.site.register(PastureStat)
admin.site.register(SceneMeta)
#admin.site.register(RasterData)
