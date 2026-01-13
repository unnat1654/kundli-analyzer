import { useState, useEffect, useRef } from 'react';
import {
  APIProvider,
  Map,
  AdvancedMarker,
  useMap,
  useMapsLibrary,
  type MapMouseEvent // Import Event type from library
  // Import Event type from library
} from '@vis.gl/react-google-maps';

interface PlaceAutocompleteProps {
  onPlaceSelect: (position: LatLng) => void;
}
export interface LatLng {
  lat: number;
  lng: number;
}


export default function MapSelector({ onLocationSelect }: {
  onLocationSelect: (location: LatLng) => void;
}) {
  // 2. Type the State with the Interface
  const [selectedPosition, setSelectedPosition] = useState<LatLng>(() => {

  const lat_str = localStorage.getItem("latitude");
  const lng_str = localStorage.getItem("longitude");
  if (lat_str && lng_str) {
    const parsed_lat = JSON.parse(lat_str) as number;
    const parsed_lng = JSON.parse(lng_str) as number;

    // Optional safety check
    if (
      typeof parsed_lat === 'number' &&
      typeof parsed_lng === 'number'
    )
      return {
        lat: parsed_lat,
        lng: parsed_lng
      } as LatLng;
    
  }
  

  // fallback default (Delhi)
  return {
    lat: 28.6139,
    lng: 77.2090,
  };
});

  useEffect(() => {
    onLocationSelect(selectedPosition);
  }, [selectedPosition, onLocationSelect]);

  // 3. Type the Event Handler
  const handleMapClick = (e: MapMouseEvent) => {
    // e.detail.latLng can be null sometimes, so we check it
    if (e.detail.latLng) {
      setSelectedPosition(e.detail.latLng);
    }
  };

  return (
    <APIProvider apiKey={import.meta.env.VITE_MAPS_API_KEY}>
      <div style={{ height: "500px", width: "100%", position: "relative" }}>

        {/* Search Bar Overlay */}
        <div>
          <PlaceAutocomplete onPlaceSelect={setSelectedPosition} />
        </div>

        {/* The Map */}
        <Map
          defaultZoom={13}
          defaultCenter={selectedPosition}
          mapId="DEMO_MAP_ID"
          onClick={handleMapClick} // Using typed handler
          disableDefaultUI={true}
        >
          <AdvancedMarker position={selectedPosition} />
        </Map>
      </div>
    </APIProvider>
  );
}


const PlaceAutocomplete = ({ onPlaceSelect }: PlaceAutocompleteProps) => {
  // 4. Type the Autocomplete instance state (It comes from the global google namespace)
  const [placeAutocomplete, setPlaceAutocomplete] = useState<google.maps.places.Autocomplete | null>(null);

  // 5. Type the Input Ref for HTML Input Element
  const inputRef = useRef<HTMLInputElement>(null);

  const places = useMapsLibrary('places');
  const map = useMap();

  useEffect(() => {
    if (!places || !inputRef.current) return;

    const options: google.maps.places.AutocompleteOptions = {
      fields: ['geometry', 'name', 'formatted_address'],
    };

    setPlaceAutocomplete(new places.Autocomplete(inputRef.current, options));
  }, [places]);

  useEffect(() => {
    if (!placeAutocomplete) return;

    const listener = placeAutocomplete.addListener('place_changed', () => {
      const place = placeAutocomplete.getPlace();

      // Safety check: geometry is optional in types, so we must check it
      if (place.geometry && place.geometry.location) {
        const lat = place.geometry.location.lat();
        const lng = place.geometry.location.lng();

        onPlaceSelect({ lat, lng });

        if (map) {
          map.panTo({ lat, lng });
          map.setZoom(15);
        }
      }
    });

    // Clean up listener to avoid memory leaks
    return () => {
      google.maps.event.removeListener(listener);
    };
  }, [onPlaceSelect, placeAutocomplete, map]);

  return (
    <input
      ref={inputRef}
      placeholder="Search for a location..."
      className="absolute top-4 left-4 z-10 w-72 rounded-lg border border-slate-300
                bg-white/90 px-4 py-2 backdrop-blur focus:ring-2 focus:ring-indigo-500"
    />
  );
};