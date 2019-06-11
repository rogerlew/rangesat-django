import json

import operator
from datetime import date, timedelta, datetime
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login

import numpy as np

from database.models import Ranch, Pasture, PastureStat, GridMetTimeSeries


def index_view(request):
    return render(request,
                  'frontend/index.html')


def ranch_view(request, ranch):
    _ranch = Ranch.objects.filter(name__contains=ranch).first()

    acquisition_date = request.GET.get('acquisition_date')
    measure = request.GET.get('measure')

    valid_measures = {'lbsperac_mean':
                          {'label': 'Mean lb/Acre Biomass',
                           'tolerance': 5000.0,
                           'cmap_name': 'viridis',
                           'range_minimum': 0.0,
                           'range_maximum': 10000.0,
                           'range_step': 10.0,
                           'source': 'pasturestats'
                          },
                      'lbsperac_percentile_10':
                          {'label': '10th percentile lb/Acre Biomass',
                           'tolerance': 5000.0,
                           'cmap_name': 'viridis',
                           'range_minimum': 0.0,
                           'range_maximum': 10000.0,
                           'range_step': 10.0,
                           'source': 'pasturestats'
                          },
                      'lbsperac_percentile_75':
                          {'label': '75th percentile lb/Acre Biomass',
                           'tolerance': 5000.0,
                           'cmap_name': 'viridis',
                           'range_minimum': 0.0,
                           'range_maximum': 10000.0,
                           'range_step': 10.0,
                           'source': 'pasturestats'
                          },
                      'lbsperac_percentile_90':
                          {'label': '90th percentile lb/Acre Biomass',
                           'tolerance': 5000.0,
                           'cmap_name': 'viridis',
                           'range_minimum': 0.0,
                           'range_maximum': 10000.0,
                           'range_step': 10.0,
                           'source': 'pasturestats'
                          },
                      'Biomass':
                          {'label': 'Gridded Biomass',
                           'tolerance': 300.0,
                           'cmap_name': 'viridis',
                           'range_minimum': 0.0,
                           'range_maximum': 10000.0,
                           'range_step': 10.0,
                           'source': 'rasterdata'
                          },
                      'NDVI':
                          {'label': 'Normalized Difference Vegetation Index',
                           'tolerance': 1.0,
                           'cmap_name': 'yignbu',
                           'range_minimum': 0.0,
                           'range_maximum': 1.0,
                           'range_step': 0.01,
                           'source': 'rasterdata'
                          }
                     }

    if measure not in valid_measures:
        measure = list(valid_measures.keys())[0]

    return render(request,
                  'frontend/ranch.html',
                  {'ranch': _ranch,
                   'acquisition_date': acquisition_date,
                   'measure': measure,
                   'valid_measures': valid_measures})


def pasture_view(request, pasture):
    _pasture = Pasture.objects.filter(pk=pasture).first()

    import matplotlib.pyplot as plt
    cmap = plt.get_cmap('plasma')

    gmtss = GridMetTimeSeries.objects.filter(pasture__pk=pasture)

    gridmet_pr_data = []
    medians = []

    for gmts in gmtss:
        dates = [d.strftime('%B %d') for d in gmts.dates]
        pr = gmts.pr_cumulative_ts__in

        gridmet_pr_data.append(dict(name=gmts.year,
                                    x=dates,
                                    y=pr.tolist(),
                                    line=dict(color=None),
                                    visible='legendonly'))

        medians.append(pr)

    gridmet_pr_data.sort(key=lambda d: d['y'][-1], reverse=True)
    for i in range(len(gridmet_pr_data)):
        if datetime.now().year == int(gridmet_pr_data[i]['name']):
            gridmet_pr_data[i]['line']['color'] = 'rgba(0.0, 0.0, 0.0, 0.4)'
            gridmet_pr_data[i]['line']['width'] = 2
            gridmet_pr_data[i]['visible'] = True
        else:
            gridmet_pr_data[i]['line']['color'] = \
                'rgba%s' % str(cmap(float(i)/(len(gridmet_pr_data)-1), alpha=0.4))


    gridmet_pr_data.sort(key=operator.itemgetter('name'))

    annual_pr_data = dict(name='Annual Precipitation',
                   x=[d['name'] for d in gridmet_pr_data],
                   y=[d['y'][-1] for d in gridmet_pr_data],
                   type='bar')

    gridmet_pr_data.sort(key=operator.itemgetter('name'), reverse=True)

    medians = [_pr[:365, None] for _pr in medians if len(_pr) > 364]
    medians = np.concatenate(medians, axis=1)
    pctl_10 = np.percentile(medians, 10, axis=1)
    pctl_90 = np.percentile(medians, 90, axis=1)
    medians = np.median(medians, axis=1)
    gridmet_pr_data.insert(0, dict(name='Median',
                                   x=[(date(2001, 1, 1) + timedelta(i)).strftime('%B %d') for i, _ in enumerate(medians)],
                                   y=medians.tolist(),
                                   line=dict(color='rgba(0.9, 0.5, 0.5, 1.0)', width=3),
                                   )
                           )

    gridmet_pr_data.insert(0, dict(name='Median',
                                   x=gridmet_pr_data[0]['x'] + gridmet_pr_data[0]['x'][::-1],
                                   y=pctl_10.tolist() + pctl_90.tolist()[::-1],
                                   fill='tozerox',
                                   fillcolor='rgba(0.4, 0.4, 0.5, 0.4)',
                                   showlegend=False,
                                   type='scatter',
                                   line=dict(color='transparent')
                                   )
                           )

    categoryarray = [(date(2000, 1, 1) + timedelta(i)).strftime('%B %d') for i in range(366)]

    biomass_trend_data = []
    shrub_biomass_annuals = None
    for analysis_type in _pasture.analysis_types:

        qs = PastureStat.objects.filter(pasture=_pasture, analysis_type=analysis_type)
        qs = sorted(qs, key=operator.attrgetter('date'))

        #dates = [str(ps.date) for ps in qs]
        #biomass = [ps.lbsperac_mean for ps in qs]

        dates = []
        biomass = []

        for ps in qs:
            if ps.lbsperac_mean >= 0.0:
                dates.append(str(ps.date))
                biomass.append(ps.lbsperac_mean)

        if analysis_type.lower() == 'shrub':
            years = sorted(set([ps.date.year for ps in qs]))

            annual_biomass = []
            for year in years:
                _days_bio_tups = [(abs((ps.date - date(year, 6, 30)).days), ps.lbsperac_mean) for ps in qs]
                annual_biomass.append(sorted(_days_bio_tups, key=lambda x: x[0])[0][1])

            shrub_biomass_annuals = dict(
                name=analysis_type,
                x=years,
                y=annual_biomass)
        else:
            biomass_trend_data.append(dict(
                name=analysis_type,
                x=dates,
                y=biomass,
                mode='lines+markers'))

    return render(request,
                  'frontend/pasture.html',
                  {'pasture': _pasture,
                   'gridmet_pr_data': json.dumps(
                       gridmet_pr_data,
                       sort_keys=True,
                       indent=4,
                       separators=(',', ': ')),
                   'biomass_trend_data': json.dumps(
                       biomass_trend_data,
                       sort_keys=True,
                       indent=4,
                       separators=(',', ': ')),
                   'shrub_biomass_annuals': json.dumps(
                       shrub_biomass_annuals,
                       sort_keys=True,
                       indent=4,
                       separators=(',', ': ')),
                   'categoryarray': json.dumps(categoryarray),
                   'annual_pr_data': annual_pr_data},
                  )


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    context = {'form': form}
    return render(request, 'registration/register.html', context)
