// 1. Define Types for Coordinates
export interface LatLng {
  lat: number;
  lng: number;
}

// --- Sub-Component Types ---
export interface PlaceAutocompleteProps {
  onPlaceSelect: (position: LatLng) => void;
}