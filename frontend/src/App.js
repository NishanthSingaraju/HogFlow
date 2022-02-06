import logo from './logo.svg';
import './App.css';
import EarthEngineMap from "./Map.js"
import DynamicForm from "./DynamicForm"
import Stack from '@mui/material/Stack';
import MapCard from "./MapCard"

function App() {
  return (
    <div className="App">
      <Stack display= "flex" direction="row" spacing={2} stye={{align_iitems: "center"}}>
      <MapCard>
        <DynamicForm></DynamicForm>
        </MapCard>
        <EarthEngineMap></EarthEngineMap>
      </Stack>
    </div>
  );
}

export default App;
