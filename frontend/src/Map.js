import {
    MapContainer,
    TileLayer,
  } from 'react-leaflet'

import MapCard from "./MapCard"
import React, { useRef, useEffect, useState } from "react";

export default function EarthEngineMap(props) {
    const ref = useRef(null);
    
    useEffect(() => {
        if (ref.current) {
            ref.current.setUrl(props.getURL);
          }
      });

    return (
        <MapCard>
        <MapContainer style={{backgroundColor: "white",height: "75vh", width: "60vw"}} center={{lat: 35.938, lng:-79.81}} zoom={10}>
             <TileLayer
                url="https://earthengine.googleapis.com/v1alpha/projects/earthengine-legacy/maps/9c2ec72e2f46dd031a99d7cdf3d9119f-1d71bccf84757b03f3acb4a2bafb7cde/tiles/{z}/{x}/{y}"
            />
             <TileLayer
                ref = {ref}
                transparent = {true}
                opacity = {0.5}
                url={props.getURL}
            />
            </MapContainer>
        </MapCard>
    )
}