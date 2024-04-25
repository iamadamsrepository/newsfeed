import './App.css';
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import {Helmet} from "react-helmet";


function ArticleDisplay(props) {
  const article = props['article'].article
  
  const provider = <div style={{background: "#7BB8B1", display: "inline-block", padding: "5px", borderRadius: "10px"}}>
    <a href={article.provider_url} target="_blank" style={{textDecoration: "none", color: "#424F63", fontWeight: "bold", fontSize: "13px", display: "flex", flexDirection: "row", alignItems: "center"}}>
      <img src={article.provider_favicon} alt="provider_icon" style={{height: "20px"}}></img>
      <div style={{width: "10px"}}></div>
      <div>{article.provider}</div>
      <div style={{width: "10px"}}></div>
    </a>
  </div>

  return <div style={{color: "#7BB8B1", padding: "15px"}}>
    {provider}
    <div style={{color: "#7BB8B1", marginTop: "5px", fontSize: "24px"}}>{article.title}</div>
    <div style={{marginTop: "5px", marginBottom: "10px"}}>{article.subtitle}</div>
    <a href={article.url} target="_blank" style={{color: "#7BB8B1", border: "2px solid #7BB8B1", borderRadius: "5px", textDecoration: "none", padding: "5px", fontSize: "11px", fontWeight: "bold"}}>To article</a>
  </div>
}

function StoryDisplayBody(props) {
  const story = props['story'].story

  const titleStyle = {
    margin: "5px 0px 5px 0px",
    fontSize: "36px"
  }

  return <div>
    <div style={titleStyle}>{story.title}</div>
    <div>{story.summary}</div>
    <div style={{margin: "15px 0px 10px 0px", fontSize: "24px", fontWeight: "bold"}}>{story.articles.length} Articles</div>
    <ul style={{listStyleType: "none", margin: 0, padding: 0}}>
      {story.articles.map(article => (<ArticleDisplay article={{article}}></ArticleDisplay>))}
    </ul>
  </div>
}

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
    background: "linear-gradient(rgba(66,79,99,0), rgba(66,79,99,1))"
  }

  return <div style={style}>
    <div style={{position: "relative"}}>
      <StoryDisplayBody story={{story}}></StoryDisplayBody>
    </div>
    <div style={fade}></div>
  </div>
}

function ExpandedStoryDisplay(props){
  const story = props['story'].story

  const style = {
    minHeight: "150px"
  }


  return <div style={style}>
    <StoryDisplayBody story={{story}}></StoryDisplayBody>
  </div>
}

function StoryDisplay(props) {
  const [expanded, setExpanded] = useState(false);

  const story = props['story'].story

  const style = {
    color: "#F0EAD6",
    whiteSpace: "normal",
    overflow: "hidden",
    margin: "40px 0px 40px 0px",
    position: "relative",
    borderTop: "2px solid #F0EAD6"
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
      const url = 'http://0.0.0.0:8000/stories'
      console.log(url)
      let response = await fetch(url)
      let json = await response.json()
      console.log(json)
      setStories(json)
    }
  }

  const storyItems = <ul style={{listStyleType: "none", padding: 0, margin: 0}}>
    {stories.map(story => <li><StoryDisplay story={{story}}/></li>)}
  </ul>;

  const header = <div style={{textAlign: "center", color: "#7BB8B1"}}><ul style={{display: "inline-block", listStyleType: "none", padding: 0, margin: "50px 0px 50px 0px"}}>
    <li><img src="./logo.png" alt="logo" style={{height: "100px"}}></img></li>
    <li style={{textAlign: "center", fontSize: "50px"}}>Digesticle</li>
    <li style={{textAlign: "center", fontSize: "25px"}}>An LLM Powered News Aggregator</li>
  </ul></div>

  return <div>
    <Helmet>
      <title>Digesticle</title>
      <meta name="description" content="Helmet application" />
      <body style="background-color: #424F63" />
    </Helmet>
    <div style={{width: "1000px", marginInline: "auto"}}>
      {/* <ul>{storyItems}</ul> */}
      <Router>
        {header}
        <div style={{height: "30px", borderTop: "2px solid #F0EAD6", borderBottom: "2px solid #F0EAD6", display: "flex", justifyContent: "space-between", alignItems: "center"}}>
          <div></div>
          <Link style={{textDecoration: "none", color: "#F0EAD6"}} to="/"><div>Stories</div></Link>
          <Link style={{textDecoration: "none", color: "#F0EAD6"}} to="/about"><div>About</div></Link>
          <div></div>
        </div>
        <Routes>
          <Route exact path="/" element={storyItems}/>
          <Route path="/about" element={<div>hello</div>}/>
        </Routes>
      </Router>
    </div>;
  </div>

}