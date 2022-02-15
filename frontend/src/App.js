import logo from './logo.svg';
import './App.css';
import EarthEngineMap from "./Map.js"
import DynamicForm from "./DynamicForm"
import Stack from '@mui/material/Stack';
import MapCard from "./MapCard"
import axios from 'axios'
import React, { useState, useEffect } from 'react';


function App() {
  const [getURL, setURL] = useState("")
  const [getSentinel, setSentinel] = useState()

  useEffect(() => {
    axios.get("http://localhost:5000/api/sentinel").then((res) => {
        setSentinel(res.data.url);
        console.log(res.data.url)
    })
  }, [])
  
  var updatefunc = ((val) => {
    setURL(val);
  });



  return (
    <div className="App">
      <Stack display= "flex"  alignItems="center" direction="row" spacing={2} stye={{align_items: "center"}}>
      <MapCard>
        <DynamicForm updateUrl = {updatefunc}></DynamicForm>
        </MapCard>
        {getSentinel && <EarthEngineMap getURL={getURL} getSentinel={getSentinel}></EarthEngineMap>}
      </Stack>
    </div>
  );
}

export default App;
