import {
    MapContainer,
    TileLayer,
  } from 'react-leaflet'

import MapCard from "./MapCard"
import React, { useRef, useEffect, useState } from "react";

export default function EarthEngineMap(props) {
    const ref = useRef(null);
    
    useEffect(() => {
        console.log(props.getSentinel)
        if (ref.current) {
            ref.current.setUrl(props.getURL);
          }
      });

    return (
        <MapCard>
        <MapContainer style={{backgroundColor: "white",height: "75vh", width: "60vw"}} center={{lat: 35.938, lng:-79.81}} zoom={10}>
             <TileLayer
                url={props.getSentinel}
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