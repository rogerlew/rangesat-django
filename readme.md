rangesat-biomass
================

Provides a database and web-based decision support tool for ranch management.

The data products of interest are:
- biomass estimates calculated from Landsat 5,7,8 surface
  reflectance products (NDVI, NBR, and NBR2),
- historical climate data from GridMET.


 == Implementation Overview


The quick explanation for how this is implemented is that it is a django project
with a Postgres11 (PostGIS) database.


 === Database/REST


 A backend with an API is built with
django-restframework. The API code resides in `rangesat.database`. REST routes
are somewhat automagically built from the models defined in
`rangesat.database.models`. Some of the model attributes are exposed as class
properties. Custom API endpoints can also be defined. e.g. a couple of those
exist in `rangesat.database.views`.

django also has some support for GIS data products and PostGIS. This allows
vector data to be stored as model attributes and things like conducting spatial
queries. There is allegedly raster support for storing rasters as blobs and
providing automated tiling and color-mapping support, but I could never get that
to work. (My best guess is a configuration issue.) So the rasters are using
`django.db.models.FileField`. For small ranches this works fine, but for larger
projects the rasters are a bit too large to make it snappy. This might need some
attention.

[https://rangesat.nkn.uidaho.edu/api/]: https://rangesat.nkn.uidaho.edu/api/


 === Frontend


django uses (can use) jinja2 templating to serve views. The frontend consists of
three pages:
- an index containing project information,
- a ranch view that is primarily spatial with a leaflet map,
- a pasture view that is primarily temporal with plotly graphs.

The ranch view has some serverside processing that occurs when a ranch is
loaded. This occurs in `rangesat.frontend.views.ranch_view` and the server-side.

The client-side exists in `rangesat/templates/frontend/ranch.html`.


 === Future


Alot of the templating is really cheating to get data into the page, so that is
something to think about if the frontend is going to exist independently of the
backend, or we keep them integrated as one project. Right now the whole site is
linked to a single database. Ideally, I think there should be a database for
user model and then separate databases for each ranch. For ease of moving
migrating things, I think the ranch databases should use sqlite3 and even file
structure for tracking rasters.

The ranch view currently loads a single ranch. Ideally, I think the ranch view
should load a set of ranches that could be specified as a get parameter:
e.g. ?ranches=['TNC', 'RCR']. I think this will also make user permissions
easier.


 === Biomass models


The database model schemas have changed from this version. The new model is
here:

[https://github.com/rogerlew/rangesat-biomass] https://github.com/rogerlew/rangesat-biomass

[Zumwalt_rangesat-biomass_output.zip] https://vandalsuidaho-my.sharepoint.com/:u:/g/personal/rogerlew_uidaho_edu/EWSIWOGCBylPk-isC0K2XcABpHArVIYaMOZm7Q4BjCq5jQ?e=AxyDly
