import './App.css';
import React, { useState, useEffect } from 'react';

function UnexpandedStoryDisplay(props) {
  const story = props['story'].story

  const style = { 
    height: "150px",
    position: "relative"
  }

  const fade = {
    position: "absolute",
    bottom: "0",
    display: "block",
    height: "50px",
    width: "100%",
    background: "linear-gradient(rgba(255,255,255,0), rgba(255,255,255,1))"
  }

  const titleStyle = {
    margin: "5px 20px 5px 20px",
    fontSize: "30px"
  }

  return <div style={style}>
    <div style={{position: "relative"}}>
      <div style={titleStyle}>{story.title}</div>
      <div style={{fontSize: "15px"}}>{story.summary}</div>
      <ul style={{margin: "4px 20px 0px 20px", fontSize: "12px", color: "navy"}}>
        {story.articles.map(article => (
          <li><a href={article.url}>{article.feed} - {article.title}</a></li>
        ))}
      </ul>
    </div>
    <div style={fade}></div>
  </div>
}

function ExpandedStoryDisplay(props){
  const story = props['story'].story

  const style = {
    minHeight: "150px"
  }

  const titleStyle = {
    margin: "5px 20px 5px 20px",
    fontSize: "30px"
  }

  return <div style={style}>
    <div style={titleStyle}>{story.title}</div>
    <div style={{fontSize: "15px"}}>{story.summary}</div>
    <ul style={{margin: "4px 20px 0px 20px", fontSize: "12px", color: "navy"}}>
      {story.articles.map(article => (
        <li><a href={article.url}>{article.feed} - {article.title}</a></li>
      ))}
    </ul>
  </div>
}

function StoryDisplay(props) {
  const [expanded, setExpanded] = useState(false);

  const story = props['story'].story

  const style = {
    color: "black",
    whiteSpace: "normal",
    overflow: "hidden",
    margin: "40px 0px 40px 0px",
    position: "relative",
    borderTop: "2px solid black"
  }

  const toggleExpanded = () => {
    if (expanded) setExpanded(false)
    else setExpanded(true)
  }

  return <div style={style} onClick={toggleExpanded}>
    {expanded
    ? <ExpandedStoryDisplay story={{story}}></ExpandedStoryDisplay>
    : <UnexpandedStoryDisplay story={{story}}></UnexpandedStoryDisplay>}
  </div>
}


export default function App() {
  const [stories, setStories] = useState([]);

  useEffect(() => {
    const asyncfn = getData
    asyncfn()
  });

  const getData = async () => {
    if (stories.length === 0) {
      const url = 'http://127.0.0.1:8000/stories'
      console.log(url)
      let response = await fetch(url)
      let json = await response.json()
      console.log(json)
      setStories(json)
    }
  }

  const storyItems = stories.map(
    story => <li><StoryDisplay story={{story}}/></li>
  );

  return <div style={{width: "1000px", marginInline: "auto"}}>
    <div style={{textAlign: "center", fontSize: "50px", margin: "50px 0px 50px 0px"}}>News Aggregator</div>
    <ul>{storyItems}</ul>
  </div>;

}