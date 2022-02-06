import {
    MapContainer,
    TileLayer,
  } from 'react-leaflet'

import MapCard from "./MapCard"

export default function EarthEngineMap() {
    return (
        <MapCard>
        <MapContainer style={{backgroundColor: "white",height: "75vh", width: "60vw"}} center={{lat: 35.938, lng:-79.81}} zoom={10}>
           
            <TileLayer
                url="https://earthengine.googleapis.com/v1alpha/projects/earthengine-legacy/maps/9c2ec72e2f46dd031a99d7cdf3d9119f-1d71bccf84757b03f3acb4a2bafb7cde/tiles/{z}/{x}/{y}"
            />
             <TileLayer
                transparent = {true}
                opacity = {0.5}
                url="https://earthengine.googleapis.com/v1alpha/projects/earthengine-legacy/maps/992a84fc73d047a04a9eaa00dc2229b0-e5bd9bd10b625505d9df0266d032f631/tiles/{z}/{x}/{y}"
            />
        </MapContainer>
        </MapCard>
    )
}