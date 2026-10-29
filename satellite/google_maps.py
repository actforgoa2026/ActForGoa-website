"""On-demand Google environmental context; no key or response caching in the UI."""
from datetime import datetime, timezone
import os
import json
from .domain import DomainError


class GoogleMaps:
    def __init__(self, client):
        self.http = client

    def _request(self, method, url, **kwargs):
        chunks, size = [], 0
        with self.http.stream(method, url, timeout=20, **kwargs) as response:
            response.raise_for_status()
            for chunk in response.iter_bytes():
                size += len(chunk)
                if size > 256_000:
                    raise ValueError('Response too large')
                chunks.append(chunk)
        return json.loads(b''.join(chunks))

    def current(self, area):
        key = os.getenv('GOOGLE_MAPS_API_KEY', '')
        if not key:
            raise DomainError('google_unavailable', 'Google environmental services are not connected yet.', 503)
        west, south, east, north = area.bbox
        location = {'latitude': (south+north)/2, 'longitude': (west+east)/2}
        result = {'location': location, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                  'attribution': 'Google Maps', 'weather': None, 'air_quality': None, 'unavailable': []}
        headers = {'X-Goog-Api-Key': key}
        # Each service may be temporarily unavailable without hiding the other.
        try:
            value = self._request('GET', 'https://weather.googleapis.com/v1/currentConditions:lookup',
                headers=headers, params={'location.latitude': location['latitude'],
                'location.longitude': location['longitude'], 'unitsSystem': 'METRIC', 'languageCode': 'en'})
            if not value.get('currentTime') or not isinstance(value.get('temperature', {}).get('degrees'), (int, float)):
                raise ValueError('Missing weather reading')
            result['weather'] = {name: value.get(name) for name in
                ('currentTime', 'temperature', 'feelsLikeTemperature', 'relativeHumidity', 'weatherCondition', 'wind', 'precipitation')}
        except Exception:
            result['unavailable'].append('Weather')
        try:
            value = self._request('POST', 'https://airquality.googleapis.com/v1/currentConditions:lookup',
                headers=headers, json={'location': location, 'universalAqi': True, 'languageCode': 'en'})
            if not value.get('dateTime') or not value.get('indexes'):
                raise ValueError('Missing air-quality reading')
            result['air_quality'] = {'dateTime': value.get('dateTime'), 'indexes': value.get('indexes', [])}
        except Exception:
            result['unavailable'].append('Air quality')
        return result
