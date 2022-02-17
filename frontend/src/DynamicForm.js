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
import TextField from '@mui/material/TextField';
import CodeModal from "./Modal.js"
import MapCard from "./MapCard.js";
import { styled } from '@mui/material/styles';
import { Card, CardContent } from '@mui/material';



class DynamicForm extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
       dataOptions:[], 
       selectedFile: null,
       openCode: false,
       formValues: [{ band : " ", rule: " ",  code: true}]
     };
    this.handleSubmit = this.handleSubmit.bind(this)
    this.handleChange = this.handleChange.bind(this)
    this.handleOpen = this.handleOpen.bind(this)
    this.handleClose = this.handleClose.bind(this)
    this.handleCode = this.handleCode.bind(this)
  }
  
  handleChange(i, e) {
    let formValues = this.state.formValues;
    if (e.props.name == "band"){
      formValues[e.props.index][e.props.name]= [e.props.value];
    } else {
      formValues[e.props.index][e.props.name]= e.props.value;
    };
    this.setState({ formValues });
    console.log(formValues)
  }

  addFormFields() {
    this.setState(({
      formValues: [...this.state.formValues, { band: "", rule: "", code: true}]
    }))
  }

  removeFormFields(i) {
    let formValues = this.state.formValues;
    formValues.splice(i, 1);
    this.setState({ formValues });
  }

  handleOpen(){
    this.setState({
      openCode: true,
    })
  }

  handleClose(){
    this.setState({
      openCode: false,
    })
  };

  handleCode(index, code, band){
    let formValues = this.state.formValues;
    formValues[index]["band"]= band;
    formValues[index]["rule"]= code;
    formValues[index]["code"]= false;
    this.setState({
      openCode: false,
      formValues: formValues
    })
  }

  async componentDidMount(){
    axios.get("http://localhost:5000/api/bands").then((res) => {
        this.setState({
          dataOptions: res.data.bands
        })
    })
  }

  async start_polling(){
    let progress = await axios.get("http://localhost:5000/api/progress");
    console.log(progress)
    if (progress.data.progress == -1){
      this.timer = null
    }
    if (this.progress != (progress.data.progress)){
    var request = {"id": progress.data.progress};

    }
  }

  async handleSubmit(i, event) {
    const request = {file: this.state.selectedFile, conditions: JSON.stringify(this.state.formValues)};
    var formData = new FormData();
    formData.append("file", this.state.selectedFile);
    formData.append("conditions", JSON.stringify(this.state.formValues))
    let proccessed = await axios.put("http://localhost:5000/api/process", formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }})
    
    axios.put("http://localhost:5000/api/URL", request,)
        .then(response => this.props.updateUrl(response.data.url)).catch(error => {
            console.error('There was an error!', error);
        });;    
  }

  styleForRule = styled('div')(({ theme }) => ({
    ...theme.typography.button,
    padding: theme.spacing(1),
    color: "white",
    fontWeight: "bold"
  }));

  onFileChange = event => {
    this.setState({selectedFile: event.target.files[0]});
  };

  fileData = () => {
    if (this.state.selectedFile) {
      return (
        <div style={{fontSize: "10px"}}>
            <p>File Name: {this.state.selectedFile.name}</p>
            <p>File Type: {this.state.selectedFile.type}</p>
        </div>
      );
    }
  }

  render() {
    return (
        <form  onSubmit={this.handleSubmit}>
          <Box display="flex" style={{flexDirection: "column nowrap", justifyContent: "space-evenly"}}>
         <TextField id="outlined-basic" label="Coordinates" variant="outlined"/>
         <input
            accept=".csv"
            style={{ display: "none" }}
            id="contained-button-file"
            type="file"
            onChange={this.onFileChange}
          />
          <label style={{display: "flex"}} htmlFor="contained-button-file">
         <Button variant="contained" component="span">
           Upload 
           </Button>
           </label>
         </Box>
          {this.state.formValues.map((element, index) => (
            <div className="form-inline" key={index}>
            {
            this.state.formValues[index]["code"] ?
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
                    <MenuItem key= {index} index = {index} name= {"band"} value={element}>{element}</MenuItem>
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
                    <MenuItem index= {index} name= {"rule"} value={"<"}>Greater Than</MenuItem>
                    <MenuItem index= {index} name= {"rule"} value={">"}>Less Than</MenuItem>
                    <MenuItem index= {index} name= {"rule"} value={"="}>=</MenuItem>
                    </Select>
                </FormControl>
            </Box>
            </Box>
            : <Card style={{ padding: 2, backgroundColor: "orange"}}><this.styleForRule>{"CUSTOM RULE"}</this.styleForRule></Card>
          }

        
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
          ))}
          
         
          <div style={{display:"flex", flexDirection:"column nowrap", justifyContent: "space-evenly"}}>
          <CodeModal index={this.state.formValues.length-1} 
            open={this.state.openCode} 
            handleOpen={this.handleOpen} 
            handleClose={this.handleClose} 
            handleCode={this.handleCode}
            suggestions={this.state.dataOptions} > 
          </CodeModal>
            <IconButton style={{color:"green", padding: 15}} variant="contained" color="primary" component="span" onClick={() => this.addFormFields()}>
            <AddIcon/>
            </IconButton>
              <Button variant="contained" onClick={() => this.handleSubmit()}>Submit</Button>
          </div>
   
          {this.fileData()}


      </form>
    );
  }
}
export default DynamicForm;