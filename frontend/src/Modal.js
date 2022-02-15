import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Modal from '@mui/material/Modal';
import CodeEditor from '@uiw/react-textarea-code-editor';
import MapCard from "./MapCard"
import { Card, CardContent } from '@mui/material';
import IconButton from '@mui/material/IconButton';
import CodeIcon from '@mui/icons-material/Code';
import Stack from '@mui/material/Stack';
import Tag from "./Tags"
import { useRef } from 'react';

const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 400,
  bgcolor: 'background.paper',
  boxShadow: 24,
  p: 4,
};

export default function CodeModal(props) {
    const [code, setCode] = React.useState(
        `def f(curr, nei): \n  pass\n`
    );

    const [bandRef, setBand] = React.useState([]);


    var submitCode = ((index, code, band) => {
      props.handleCode(index, code, band)
      setCode(`def f(curr, nei): \n  pass\n`)
    });

    var setBandRef = ((tags) => {
      var arr = [];
      for (var tag in tags) {
          arr.push(tags[tag]["id"])
        }
        setBand(arr);
      }
    );


  return (
    <div>
      <IconButton style={{color:"orange", padding: 15}} variant="contained" color="primary" component="span" onClick={props.handleOpen}>
          <CodeIcon/>
        </IconButton>
      <Modal
        open={props.open}
        onClose={props.handleClose}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
      >
        
        <Card sx={style}>
        <Stack display= "flex" direction="column" spacing={2}>
          <Tag bandRef={setBandRef}></Tag>
          <CodeEditor
            value={code}
            language="python"
            placeholder="Please enter Python code."
            onChange={(evn) => setCode(evn.target.value)}
            padding={15}
            style={{
            fontSize: 14,
            backgroundColor: "#f5f5f5",
            fontFamily: 'ui-monospace,SFMono-Regular,SF Mono,Consolas,Liberation Mono,Menlo,monospace',
          }}/>
          <Button variant="contained" onClick={() => submitCode(props.index, code, bandRef)}>Upload</Button>
          </Stack>
        </Card>
      </Modal>
    </div>
  );
}
