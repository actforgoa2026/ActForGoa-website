/// <reference types="google.maps" />
import { useEffect, useRef, useState } from 'react';
import { importLibrary } from '@googlemaps/js-api-loader';
import { MapPin } from 'lucide-react';
import { Button } from './components/arc/button/button';
import { Alert } from './components/arc/alert/alert';

import { loadGoogleMap } from './google-map';

type Coordinates = [number, number] | null;
type Props = { coordinates: Coordinates; onPin: (lat: number, lng: number) => boolean };
const positionOf = (coordinates: Coordinates) => coordinates ? { lat: coordinates[0], lng: coordinates[1] } : null;

export default function GooglePlaceMap({ coordinates, onPin }: Props) {
  const node = useRef<HTMLDivElement>(null);
  const map = useRef<google.maps.Map | null>(null);
  const marker = useRef<google.maps.marker.AdvancedMarkerElement | null>(null);
  const pin = useRef(onPin);
  const currentCoordinates = useRef(coordinates);
  pin.current = onPin;
  currentCoordinates.current = coordinates;
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState(false);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (!node.current) return;
    let cancelled = false;
    let loadFailed = false;
    const listeners: google.maps.MapsEventListener[] = [];
    setReady(false);
    setFailed(false);
    const fail = () => {
      if (cancelled) return;
      loadFailed = true;
      setFailed(true);
      setReady(false);
    };
    const timeout = window.setTimeout(fail, 20000);
    const authWindow = window as typeof window & { gm_authFailure?: () => void };
    const previousFailure = authWindow.gm_authFailure;
    const authFailure = () => { fail(); previousFailure?.(); };
    authWindow.gm_authFailure = authFailure;

    loadGoogleMap().then(async mapsLibrary => {
      const markerLibrary = await importLibrary('marker');
      if (cancelled || loadFailed || !node.current) return;
      const { Map } = mapsLibrary as google.maps.MapsLibrary;
      const { AdvancedMarkerElement } = markerLibrary as google.maps.MarkerLibrary;
      const initial = positionOf(currentCoordinates.current);
      const view = new Map(node.current, {
        center: initial || { lat: 15.35, lng: 74.02 },
        zoom: initial ? 14 : 10,
        mapId: 'DEMO_MAP_ID',
        gestureHandling: 'cooperative',
        restriction: { latLngBounds: { south: 14.8, west: 73.5, north: 15.9, east: 74.5 }, strictBounds: true },
        zoomControl: true,
        cameraControl: false,
        streetViewControl: false,
        mapTypeControl: false,
        fullscreenControl: false,
      });
      const selected = new AdvancedMarkerElement({
        map: view,
        title: 'Selected heritage place. Drag to adjust the pin.',
        position: initial,
        gmpDraggable: true,
      });
      map.current = view;
      marker.current = selected;
      const choose = (point: google.maps.LatLng | null | undefined) => {
        if (!point) return;
        // Rejected drops must return to the last valid pin rather than show a different place.
        selected.position = pin.current(point.lat(), point.lng()) ? point : positionOf(currentCoordinates.current);
      };
      listeners.push(view.addListener('click', (event: google.maps.MapMouseEvent) => {
        event.stop();
        choose(event.latLng);
      }));
      listeners.push(selected.addListener('dragend', (event: google.maps.MapMouseEvent) => choose(event.latLng)));
      listeners.push(view.addListener('idle', () => {
        if (!cancelled && !loadFailed) {
          window.clearTimeout(timeout);
          setReady(true);
        }
      }));
    }).catch(fail);

    return () => {
      cancelled = true;
      window.clearTimeout(timeout);
      listeners.forEach(listener => listener.remove());
      if (marker.current) marker.current.map = null;
      marker.current = null;
      map.current = null;
      if (authWindow.gm_authFailure === authFailure) authWindow.gm_authFailure = previousFailure;
    };
  }, [attempt]);

  useEffect(() => {
    if (!ready || !marker.current) return;
    const position = positionOf(coordinates);
    marker.current.position = position;
    if (position && !map.current?.getBounds()?.contains(position)) map.current?.panTo(position);
  }, [ready, coordinates?.[0], coordinates?.[1]]);

  return <>
    <p id="heritage-map-help">Click or tap a public place to drop a pin. Drag the pin to adjust it. On phones, use two fingers to move the map.</p>
    <div className="heritage-map" ref={node} aria-label="Google map of heritage places in Goa" aria-describedby="heritage-map-help" hidden={failed}/>
    {failed ? <>
      <Alert tone="warning" title="Google Maps could not load">Your story is still here. Try the map again, or continue with the place name.</Alert>
      {<Button type="button" variant="secondary" onClick={() => setAttempt(value => value + 1)}>Try map again</Button>}
    </> : <>
      <Button type="button" variant="secondary" disabled={!ready} onClick={() => {
        const center = map.current?.getCenter();
        if (center) onPin(center.lat(), center.lng());
      }}><MapPin size={18}/>{ready ? 'Pin map centre' : 'Loading Google Maps…'}</Button>
      <p className="heritage-map-keyboard">Using a keyboard? Move the map with the arrow keys, then choose “Pin map centre”.</p>
    </>}
  </>;
}
