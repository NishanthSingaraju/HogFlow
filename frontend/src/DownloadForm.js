import React from "react";
import FormControl from '@mui/material/FormControl';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import AddIcon from '@mui/icons-material/Add';
import IconButton from '@mui/material/IconButton';
import RemoveCircleIcon from '@mui/icons-material/RemoveCircle';
import Button from '@mui/material/Button';
import axios from 'axios'
import TextField from '@mui/material/TextField';

class DownloadForm extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
           formValues: [{type: " ", dataset : " "}]
         };
      }

      async handleSubmit(i, event) {
          console.log(event)
      }
      
      handleChange(i, e) {
        let formValues = this.state.formValues;
        formValues[e.props.index][e.props.name]= e.props.value;
        this.setState({ formValues });
        console.log(formValues)
      }

      render() {
        return(
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
                          {this.state.dataOptions.map((element) => (
                        <MenuItem key= {index} index = {index} name= {"dataset"} value={element}>{element}</MenuItem>
                          ))}
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
                        <MenuItem index= {index} name= {"type"} value={"<"}>Greater Than</MenuItem>
                        <MenuItem index= {index} name= {"type"} value={">"}>Less Than</MenuItem>
                        <MenuItem index= {index} name= {"type"} value={"="}>=</MenuItem>
                        </Select>
                    </FormControl>
                </Box>
                </Box>
                  {
                    index ? 
                    <Box style={{display:"flex", flexDirection:"column nowrap", justifyContent: "space-evenly"}}>
                    <IconButton style={{color:"red"}} variant="contained" color="primary" component="span" onClick={() => this.removeFormFields(index)}>
                      <RemoveCircleIcon/>
                    </IconButton>
                    </Box>
                    : null
                  }
                </div>
              )
        )
      }
            </form>
      )
    }
}

export default DownloadForm;