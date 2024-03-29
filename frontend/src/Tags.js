import React, { useState, useEffect } from 'react';
import { render } from 'react-dom';
import { WithContext as ReactTags } from 'react-tag-input';
import { Box } from '@mui/material';


const KeyCodes = {
  comma: 188,
  enter: 13
};

const delimiters = [KeyCodes.comma, KeyCodes.enter];

export default function Tags(props){
  const [tags, setTags] = React.useState([]);
  const [suggestions, setSuggest] = React.useState([{"id": "Here", "text": "Here"}]);

  const handleDelete = i => {
    setTags(tags.filter((tag, index) => index !== i));
  };

  const handleAddition = tag => {
    setTags([...tags, tag]);
  };

  useEffect(() => {
    props.bandRef(tags); 
    }, [tags])

  useEffect(() => {
    let data = Array.from(props.suggestions);
    let result = data.map(suggestion => {
      return {
        id: suggestion,
        text: suggestion
      }
    })
    console.log(result)
    setSuggest(result)
   }, [props.suggestions])
    

  const handleDrag = (tag, currPos, newPos) => {
    const newTags = tags.slice();
    newTags.splice(currPos, 1);
    newTags.splice(newPos, 0, tag);

    // re-render
    setTags(newTags);
  };

  const handleTagClick = index => {
    console.log(tags)
    console.log('The tag at index ' + index + ' was clicked');
  };

  return (
        <ReactTags
          inputFieldPosition="inline"
          style={{display:"flex", flexDirection: "column nowrap", position: 'relative', justifyContent: "space-evenly"}}
          tags={tags}
          suggestions={suggestions}
          delimiters={delimiters}
          handleDelete={handleDelete}
          handleAddition={handleAddition}
          handleDrag={handleDrag}
          handleTagClick={handleTagClick}
          autocomplete
        />
  );
};
