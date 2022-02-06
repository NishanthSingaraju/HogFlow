import React from "react";
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import AddIcon from '@mui/icons-material/Add';
import IconButton from '@mui/material/IconButton';
import RemoveCircleIcon from '@mui/icons-material/RemoveCircle';
import Button from '@mui/material/Button';
import axios from 'axios'

class DynamicForm extends React.Component {
  constructor(props) {
    super(props)
    this.state = { 
       formValues: [{ band : " ", rule: " " }]
     };
    this.handleSubmit = this.handleSubmit.bind(this)
    this.handleChange = this.handleChange.bind(this)
  }
  
  handleChange(i, e) {
    let formValues = this.state.formValues;
    formValues[e.props.index][e.props.name] = e.props.value;
    this.setState({ formValues });
    console.log(formValues)
  }

  addFormFields() {
    this.setState(({
      formValues: [...this.state.formValues, { band: "", rule: "" }]
    }))
  }

  removeFormFields(i) {
    let formValues = this.state.formValues;
    formValues.splice(i, 1);
    this.setState({ formValues });
  }

  handleSubmit(i, event) {
    const request = {conditions: JSON.stringify(this.state.formValues)};
    axios.put("http://localhost:5000/api/URL", request)
        .then(response => this.props.updateUrl(response.data.url)).catch(error => {
            console.error('There was an error!', error);
        });;
        
    
  }

  render() {
    return (
        <form  onSubmit={this.handleSubmit}>
          {this.state.formValues.map((element, index) => (
            <div className="form-inline" key={index}>
            <Box display="flex" style={{flexDirection: "column nowrap", justifyContent: "space-evenly", padding: 6}}>
            <Box sx={{ minWidth: 150, padding: 1}}>
                <FormControl fullWidth>
                    <InputLabel id="Bands"></InputLabel>
                    <Select
                    id="Bands"
                    value={this.state.formValues[index]["band"]}
                    onChange={this.handleChange}
                    >
                    <MenuItem index= {index} name= {"band"} value={"elv"}>Elevation</MenuItem>
                    <MenuItem index= {index} name= {"band"} value={"soil"}>Soil Type</MenuItem>
                    <MenuItem index= {index} name= {"band"} value={"discharge"}>Discharge</MenuItem>
                    </Select>
                </FormControl>
            </Box>
            <Box sx={{ minWidth: 150, padding: 1}}>
                <FormControl fullWidth>
                    <InputLabel id="rule"></InputLabel>
                    <Select
                    id="Rule"
                    value={this.state.formValues[index]["rule"]}
                    onChange={this.handleChange}
                    >
                    <MenuItem index= {index} name= {"rule"} value={"<"}>Greater Than</MenuItem>
                    <MenuItem index= {index} name= {"rule"} value={">"}>Less Than</MenuItem>
                    </Select>
                </FormControl>
            </Box>
            </Box>

              {
                index ? 
                
                <IconButton style={{color:"red"}} variant="contained" color="primary" aria-label="upload picture" component="span" onClick={() => this.removeFormFields(index)}>
                  <RemoveCircleIcon/>
                </IconButton>

                : null
              }
            </div>
          ))}


          <div className="button-section">
            <IconButton style={{color:"green", padding: 15}} variant="contained" color="primary" aria-label="upload picture" component="span" onClick={() => this.addFormFields()}>
            <AddIcon/>
            </IconButton>
              <Button variant="contained" onClick={() => this.handleSubmit()}>Submit</Button>
          </div>


      </form>
    );
  }
}
export default DynamicForm;