"""Package a recorded, real comparison for operator import; never calls providers.

The output is a saved example, not evidence of this deployment's retrieval access.
Raw rasters are deliberately not reconstructed from the committed PNG previews.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from satellite.summary import summarize_comparison, canopy_presence


def recorded_example():
    directory=ROOT/'reports/satellite-live-2026-10-28'
    validation=json.loads((directory/'validation.json').read_text())
    if validation['state']!='passed' or any(r['status']!=200 for r in validation['requests']):
        raise ValueError('Recorded provider verification did not pass.')
    observations={}
    for record in validation['observations']:
        png=(directory/(record['label']+'.png')).read_bytes()
        if hashlib.sha256(png).hexdigest()!=record['png_sha256']:
            raise ValueError('Recorded image no longer matches its verified hash.')
        observations[record['label']]={**record['provenance'],'quality':record['quality'],'image':'data:image/png;base64,'+base64.b64encode(png).decode()}
    before,after=validation['selected_scene_ids']
    request={**validation['request'],'before_id':before,'after_id':after,'intent':'canopy_loss',
        'question':'Recorded real comparison: tree canopy, 10–20 October 2026',
        'window_start':'2026-10-18','window_end':'2026-10-28'}
    interval={'before':observations['before']['acquired_at'][0],'after':observations['after']['acquired_at'][0],
        'query_window_relation':'overlaps_window','exact_event_date':None,'cause':'not_established'}
    classification={'state':'unavailable','answers':{},'message':'AI image decisions are unavailable. No model classification was performed for this recorded comparison.'}
    evidence=validation['comparison']
    result={**observations,'intent':'canopy_loss','evidence':evidence,'classification':classification,
        'summary':summarize_comparison('canopy_loss',evidence,classification,interval),
        'canopy_presence':canopy_presence(evidence,classification),'observation_interval':interval,
        'area':{'geometry':validation['grid']['wgs84_geometry'],'area_m2':round(validation['grid']['area_m2']),'clipped_to_goa':validation['grid']['clipped_to_goa']},
        'generated_at':validation['finished_at'],
        'recorded_example':{'kind':'recorded-real','retrieved_at':validation['finished_at'],
            'source_url':'https://github.com/actforgoa2026/ActForGoa-website/blob/deb1f1d1e54d828f1463da787e9b75dd2e4aea45/reports/satellite-live-2026-10-28/README.md',
            'note':'Imported from the earlier verified Copernicus retrieval. This Railway deployment has not retrieved new imagery. Measurements are the recorded numeric comparison; no raw raster reprocessing or AI classification was performed during import.'},
        'fire_detections':{'state':'not_queried','message':'FIRMS has not been queried; no conclusion about absence of fire is supported.'},
        'library_context':{'state':'unavailable','message':'No ecology-library context was retrieved for this saved example.','sources':[]},
        'limitations':['This example covers one selected area, not statewide monitoring.',
            'No vegetation-loss patches met the exploratory thresholds; this does not establish absence of tree removal.',
            'Individual-tree counts, exact event dates and causes are not established.',
            'The recorded measurements have not passed representative Goa field validation.']}
    return {'request':request,'result':result,'created_at':validation['finished_at'],
            'source_sha256':hashlib.sha256((directory/'validation.json').read_bytes()).hexdigest()}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    target=Path(args.output)
    with target.open('x')as file:json.dump(recorded_example(),file,allow_nan=False)
    print('Packaged hash-verified recorded real imagery. No provider calls were made.')
