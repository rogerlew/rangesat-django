import uuid

import requests
import shutil
from enum import Enum

import json

from pprint import pprint

import numpy as np

import netCDF4

from all_your_base import RasterDatasetInterpolator


class GridMetVariable(Enum):
    Precipitation = 1
    MinimumTemperature = 2
    MaximumTemperature = 3
    SurfaceRadiation = 4
    PalmarDroughtSeverityIndex = 5
    PotentialEvapotranspiration = 6
    BurningIndex = 7


_var_meta = {
    GridMetVariable.Precipitation: ('pr', 'precipitation_amount'),
    GridMetVariable.MinimumTemperature: ('tmmn', 'air_temperature'),
    GridMetVariable.MaximumTemperature: ('tmmx', 'air_temperature'),
    GridMetVariable.SurfaceRadiation: ('srad', 'surface_downwelling_shortwave_flux_in_air'),
    GridMetVariable.PalmarDroughtSeverityIndex: ('pdsi', 'palmer_drought_severity_index'),
    GridMetVariable.PotentialEvapotranspiration: ('pet', 'potential_evapotranspiration'),
    GridMetVariable.BurningIndex: ('bi', 'burning_index_g'),
}


def nc_extract(fn, locations):
    rds = RasterDatasetInterpolator(fn, proj='EPSG:4326')

    d = {}
    for lng, lat, pk in locations:
        data = rds.get_location_info(lng, lat, 'nearest')

        d[pk] = data

    return d


def _retrieve(gridvariable: GridMetVariable, bbox, year):
    global _var_meta

    abbrv, variable_name = _var_meta[gridvariable]

    assert len(bbox) == 4
    west, north, east, south = [float(v) for v in bbox]
    assert east > west
    assert south < north

    url = 'http://thredds.northwestknowledge.net:8080/thredds/ncss/MET/{abbrv}/{abbrv}_{year}.nc?'\
          'var={variable_name}&'\
          'north={north}&west={west}&east={east}&south={south}&'\
          'disableProjSubset=on&horizStride=1&'\
          'time_start={year}-01-01T00%3A00%3A00Z&'\
          'time_end={year}-12-31T00%3A00%3A00Z&'\
          'timeStride=1&accept=netcdf'\
          .format(year=year, east=east, west=west, south=south, north=north,
                  abbrv=abbrv, variable_name=variable_name)

    referer = 'https://rangesat.nkn.uidaho.edu'
    s = requests.Session()
    response = s.get(url, headers={'referer': referer}, stream=True)
    id = uuid.uuid4()
    with open('/home/weppdev/PycharmProjects/rangesat/climate/gridmet/temp/%s.nc' % id, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

    return id


def retrieve_timeseries(variables, locations, start_year, end_year):
    global _var_meta

    lons = [loc[0] for loc in locations]
    lats = [loc[1] for loc in locations]
    
    ll_x, ll_y = min(lons), min(lats)
    ur_x, ur_y = max(lons), max(lats)

    bbox = [ll_x, ur_y, ur_x, ll_y]

    start_year = int(start_year)
    end_year = int(end_year)

    assert start_year <= end_year

    d = {}
    for gridvariable in variables:
        for year in range(start_year, end_year + 1):
            print('acquiring', gridvariable, year)
            id = _retrieve(gridvariable, bbox, year)
            fn = '/home/weppdev/PycharmProjects/rangesat/climate/gridmet/temp/%s.nc' % id
            print('extracting locations from', fn)
            _d = nc_extract(fn, locations)

            abbrv, variable_name = _var_meta[gridvariable]
            ds = netCDF4.Dataset(fn)
            variable = ds.variables[variable_name]
            desc = variable.description
            units = variable.units

            if _d is None:
                for lon, lat, pk in locations:
                    d[(abbrv, year, pk)] = (None, desc, units)
            else:
                for pk, ts in _d.items():
                    d[(abbrv, year, pk)] = (ts, desc, units)

    return d


#if __name__ == "__main__":
from database.models import  GridMetTimeSeries, Pasture, Ranch

ranch = Ranch.objects.filter(name='TNC').first()

pastures = ranch.pastures

locations = []
for p in pastures:
    locations.append((p.centroid.x, p.centroid.y, p.pk))

start_year = 1979
end_year = 2019

d = retrieve_timeseries([var for var in GridMetVariable],
                        locations, start_year, end_year)

print(d)


for p in pastures:
    for year in range(start_year, end_year+1):
        pr_ts, pr_desc, pr_units = d['pr', year, p.pk]
        tmmn_ts, tmmn_desc, tmmn_units = d['tmmn', year, p.pk]
        tmmx_ts, tmmx_desc, tmmx_units = d['tmmx', year, p.pk]
        srad_ts, srad_desc, srad_units = d['srad', year, p.pk]
        pdsi_ts, pdsi_desc, pdsi_units = d['pdsi', year, p.pk]
        pet_ts, pet_desc, pet_units = d['pet', year, p.pk]
        bi_ts, bi_desc, bi_units = d['bi', year, p.pk]

        pr_ts = np.array(pr_ts)
        tmmn_ts = np.array(tmmn_ts)
        tmmx_ts = np.array(tmmx_ts)
        srad_ts = np.array(srad_ts)
        pdsi_ts = np.array(pdsi_ts)
        pet_ts = np.array(pet_ts)
        bi_ts = np.array(bi_ts)

        gdata, _ = GridMetTimeSeries.objects.get_or_create(
            pasture=p,
            ranch=ranch,
            lon=p.centroid.x,
            lat=p.centroid.y,
            year=year,
            pr=pr_ts.tobytes(),
            pr_description=pr_desc,
            pr_dtype=str(pr_ts.dtype),
            pr_units=pr_units,
            tmmn=tmmn_ts.tobytes(),
            tmmn_description=tmmn_desc,
            tmmn_dtype=str(tmmn_ts.dtype),
            tmmn_units=tmmn_units,
            tmmx=tmmx_ts.tobytes(),
            tmmx_description=tmmx_desc,
            tmmx_dtype=str(tmmx_ts.dtype),
            tmmx_units=tmmx_units,
            srad=srad_ts.tobytes(),
            srad_description=srad_desc,
            srad_dtype=str(srad_ts.dtype),
            srad_units=srad_units,
            pet=pet_ts.tobytes(),
            pet_description=pet_desc,
            pet_dtype=str(pet_ts.dtype),
            pet_units=pet_units,
            pdsi=pdsi_ts.tobytes(),
            pdsi_description=pdsi_desc,
            pdsi_dtype=str(pdsi_ts.dtype),
            pdsi_units=pdsi_units,
            bi=bi_ts.tobytes(),
            bi_description=bi_desc,
            bi_dtype=str(bi_ts.dtype),
            bi_units=bi_units
        )
        gdata.save()


# exec(open('/home/weppdev/PycharmProjects/rangesat/climate/gridmet/client.py').read())