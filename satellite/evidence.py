"""Numeric reflectance comparison on identical grids, before any language model."""
import base64
import io
import numpy as np
from PIL import Image
from rasterio.features import geometry_mask, shapes
from rasterio.io import MemoryFile
from rasterio.transform import from_origin, array_bounds
from rasterio.warp import calculate_default_transform, reproject, transform_bounds, Resampling
from shapely.geometry import shape, mapping
from shapely.ops import transform
from .domain import DomainError, TO_WGS


def read_observation(data: bytes, grid: dict):
    with MemoryFile(data) as mem, mem.open() as dataset:
        expected = from_origin(grid['bounds'][0], grid['bounds'][3], 10, 10)
        if dataset.count != 8 or dataset.width != grid['width'] or dataset.height != grid['height'] or dataset.crs is None or dataset.crs.to_epsg() != 32643 or not dataset.transform.almost_equals(expected):
            raise DomainError('unaligned_imagery', 'The imagery does not match the requested geographic grid.', 502)
        bands = dataset.read()
    roi = geometry_mask([grid['geometry']], out_shape=bands.shape[1:], transform=expected, invert=True)
    valid = (bands[7] == 1) & np.isfinite(bands).all(axis=0) & roi
    clear = valid & np.isin(bands[6], [4, 5, 6])
    # Buffer suspect pixels by 20 m. SCL itself is only native 20 m resolution.
    suspect = valid & ~np.isin(bands[6], [4, 5, 6])
    buffered = np.zeros_like(suspect)
    padded = np.pad(suspect, 2)
    for y in range(5):
        for x in range(5):
            buffered |= padded[y:y+suspect.shape[0], x:x+suspect.shape[1]]
    clear &= ~buffered
    # EVE's true_color preset uses B04/B03/B02, gain 2.5; no numerical index is computed from this image.
    rgb = np.clip(np.nan_to_num(bands[:3]).transpose(1, 2, 0) * 2.5 * 255, 0, 255).astype('uint8')
    rgba = np.dstack([rgb, (valid * 255).astype('uint8')])
    png = io.BytesIO(); Image.fromarray(rgba).save(png, format='PNG')
    total = int(roi.sum())
    stats = {'usable_fraction': round(float(clear.sum()) / max(total, 1), 4),
             'missing_fraction': round(float((roi & ~valid).sum()) / max(total, 1), 4),
             'cloud_shadow_or_uncertain_fraction': round(float((valid & ~clear).sum()) / max(total, 1), 4)}
    return {'bands': bands, 'clear': clear, 'roi': roi, 'png': png.getvalue(), 'quality': stats, 'transform': expected}


def index(a, b):
    denominator = a+b
    return np.divide(a-b, denominator, out=np.full_like(a, np.nan), where=np.abs(denominator) > 1e-6)


def compare_pixels(before, after, grid):
    common = before['clear'] & after['clear']
    total = int(before['roi'].sum())
    comparable = float(common.sum())/max(total, 1)
    result = {'common_usable_fraction': round(comparable, 4), 'state': 'observable' if comparable >= .8 else 'insufficient_clear_coverage',
              'metrics': {}, 'candidates': {'type': 'FeatureCollection', 'features': []},
              'water_change':None,'water_candidates':{'type':'FeatureCollection','features':[]},
              'method': 'Exploratory reflectance changes; thresholds require Goa field validation. Vegetation is not necessarily tree canopy.'}
    if common.sum() < 9:
        return result
    water_before=common & (before['bands'][6]==6)
    water_after=common & (after['bands'][6]==6)
    gained=water_after & ~water_before
    lost=water_before & ~water_after
    result['water_change']={'before_area_m2':int(water_before.sum())*100,'after_area_m2':int(water_after.sum())*100,
        'gained_area_m2':int(gained.sum())*100,'lost_area_m2':int(lost.sum())*100,
        'method':'Area classified as water by Sentinel-2 SCL on common usable pixels. Native 20 m classification; not river flow, water quality or a surveyed shoreline.'}
    for mask,kind in [(gained,'possible_surface_water_gain'),(lost,'possible_surface_water_loss')]:
        for geom,value in shapes(mask.astype('uint8'),mask=mask,transform=before['transform'],connectivity=4):
            polygon=shape(geom)
            if value==1 and polygon.area>=900:
                result['water_candidates']['features'].append({'type':'Feature','geometry':mapping(transform(TO_WGS,polygon)),
                    'properties':{'kind':kind,'area_m2':round(polygon.area),'cause':'not_established','review':'required'}})
    result['water_candidates']['features'].sort(key=lambda f:-f['properties']['area_m2'])
    result['water_candidates_truncated']=len(result['water_candidates']['features'])>100
    result['water_candidates']['features']=result['water_candidates']['features'][:100]
    indices = []
    for observation in (before, after):
        red, green, blue, nir, swir1, swir2 = observation['bands'][:6]
        indices.append({'ndvi': index(nir, red), 'ndwi': index(green, nir), 'nbr': index(nir, swir2)})
    for key in ('ndvi', 'ndwi', 'nbr'):
        usable = common & np.isfinite(indices[0][key]) & np.isfinite(indices[1][key])
        if usable.any():
            a, b = indices[0][key][usable], indices[1][key][usable]
            result['metrics'][key] = {'before_median': round(float(np.median(a)), 4), 'after_median': round(float(np.median(b)), 4),
                                      'median_paired_change': round(float(np.median(b-a)), 4), 'paired_pixels': int(usable.sum())}
    loss = common & (indices[0]['ndvi'] >= .6) & (indices[0]['ndvi']-indices[1]['ndvi'] >= .25)
    for geom, value in shapes(loss.astype('uint8'), mask=loss, transform=before['transform'], connectivity=4):
        polygon = shape(geom)
        if value != 1 or polygon.area < 900:
            continue
        result['candidates']['features'].append({'type': 'Feature', 'geometry': mapping(transform(TO_WGS, polygon)),
            'properties': {'kind': 'possible_vegetation_loss', 'area_m2': round(polygon.area),
                           'cause': 'not_established', 'review': 'required'}})
    # Bound output; tell callers explicitly when candidate reporting is partial.
    result['candidates']['features'].sort(key=lambda f: -f['properties']['area_m2'])
    result['candidates_truncated'] = len(result['candidates']['features']) > 100
    result['candidates']['features'] = result['candidates']['features'][:100]
    return result


def map_layer(observation):
    """Reproject display pixels onto Web Mercator before Leaflet imageOverlay.

    A north-up UTM image is rotated relative to Web Mercator: stretching the
    original PNG to longitude/latitude corners would misplace its pixels. Keep
    the original reflectance/masks unchanged for analysis and warp only RGBA.
    """
    rgba = np.asarray(Image.open(io.BytesIO(observation['png'])).convert('RGBA'))
    height, width = rgba.shape[:2]
    bounds = array_bounds(height, width, observation['transform'])
    target_transform, target_width, target_height = calculate_default_transform(
        'EPSG:32643', 'EPSG:3857', width, height, *bounds)
    output = np.zeros((4, target_height, target_width), dtype='uint8')
    for band in range(4):
        reproject(rgba[:, :, band], output[band], src_transform=observation['transform'],
                  src_crs='EPSG:32643', dst_transform=target_transform,
                  dst_crs='EPSG:3857', src_nodata=0, dst_nodata=0, resampling=Resampling.nearest)
    png = io.BytesIO()
    Image.fromarray(output.transpose(1, 2, 0)).save(png, format='PNG')
    geographic = transform_bounds('EPSG:3857', 'EPSG:4326',
                                  *array_bounds(target_height, target_width, target_transform))
    return {'image': 'data:image/png;base64,' + base64.b64encode(png.getvalue()).decode(),
            'bbox': list(geographic), 'bbox_crs': 'EPSG:4326', 'crs': 'EPSG:3857',
            'width': target_width, 'height': target_height,
            'note': 'Display reprojected to Web Mercator. Measurements use the original 10 m UTM grid.'}


def public_observation(observation, provenance):
    display = map_layer(observation)
    image = display.pop('image')
    # One display image serves the map and side-by-side viewer. Native PNGs
    # remain internal for classification; duplicating both projections would
    # exceed hosted proxy limits for otherwise valid areas.
    return {**provenance, 'quality': observation['quality'],
            'image': image, 'map_layer': display}


def classification_image(observation, common):
    """Mask exactly the same unusable pixels in both model images with neutral grey."""
    image = np.array(Image.open(io.BytesIO(observation['png'])).convert('RGB'))
    image[~common] = [128, 128, 128]
    output = io.BytesIO()
    Image.fromarray(image).save(output, format='PNG')
    return output.getvalue()
