from subprocess import Popen, PIPE
import os
from os.path import exists as _exists
from .locationinfo import RasterDatasetInterpolator

from osgeo import osr

wgs84_proj4 = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'


def wkt_2_proj4(wkt_text):
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt_text)
    proj4 = srs.ExportToProj4().strip()
    return proj4


def warp2wgs(fn):
    dst = fn.split('.')
    dst.insert(-1, 'wgs')
    dst = '.'.join(dst)

    if _exists(dst):
        os.remove(dst)

    cmd = ['gdalwarp', '-t_srs', wgs84_proj4,
           '-r', 'near', fn, dst]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    p.wait()

    assert _exists(dst)

    return dst
