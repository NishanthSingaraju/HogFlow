import logo from './logo.svg';
import './App.css';
import EarthEngineMap from "./Map.js"
import DynamicForm from "./DynamicForm"
import Stack from '@mui/material/Stack';
import MapCard from "./MapCard"
import React, { useState, useEffect } from 'react';


function App() {
  const [getURL, setURL] = useState("")

  var updatefunc = ((val) => {
    setURL(val);
  });

  return (
    <div className="App">
      <Stack display= "flex" direction="row" spacing={2} stye={{align_iitems: "center"}}>
      <MapCard>
        <DynamicForm updateUrl = {updatefunc}></DynamicForm>
        </MapCard>
        <EarthEngineMap getURL={getURL}></EarthEngineMap>
      </Stack>
    </div>
  );
}

export default App;
