import React from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import { Helmet } from "react-helmet";
import { useState, useEffect } from "react";

import StoriesList from "./StoriesList"
import StoryPage from "./StoryPage"
import { apiHost, colors } from "./config";

function App() {
  const [stories, setStories] = useState([]);

  useEffect(() => {
    const getData = async () => {
      if (stories.length === 0) {
        console.log("fetching data");
        const url = apiHost + "/stories";
        let response = await fetch(url);
        let stories = await response.json();
        stories.forEach((story) => {
          story.n_articles = story.articles.length;
        });
        setStories(stories);
        console.log(stories);
      }
    };
    getData();
  }, [stories]);

  const about = (
    <div style={{ margin: "10px", padding: "10px", lineHeight: "1.6", backgroundColor: "rgba(255, 255, 255, 0.1)" }}>
      <h2>About Digesticle</h2>
      <p>
        📰 <strong>Only the Most Important Stories, Condensed for You</strong>
      </p>
      <p>
        <strong>AI-Powered Curation 🔥</strong> – We scan thousands of news sources to surface only the most critical
        breaking stories, so you don’t have to.
      </p>
      <p>
        <strong>Trusted Journalism 🏆</strong> – No sensationalism, no fluff—just credible news from the world’s most
        respected outlets.
      </p>
      <p>
        <strong>Pre-Digested Summaries ✍️</strong> – No more sifting through long articles. Our AI extracts the key
        facts, context, and takeaways in just a few bullet points.
      </p>
      <p>
        🌍 <strong>The Full Picture, In Seconds</strong>
      </p>
      <p>
        <strong>Multi-Source Perspectives 📡</strong> – See how different outlets report on the same event to get a
        well-rounded view.
      </p>
      <p>
        <strong>Bias Awareness 🎭</strong> – Instantly detect political leanings and credibility scores for every story.
      </p>
      <p>
        <strong>Real-Time Updates ⏳</strong> – Stay ahead with AI-driven tracking of developing news, so you’re always
        informed.
      </p>
      <p>
        🔎 <strong>Fast. Intelligent. No Noise.</strong>
      </p>
      <p>
        No clickbait. No distractions. No endless scrolling—just what matters. News that’s fast, transparent, and to the
        point.
      </p>
    </div>
  );

  return (
    <Router>
      <div
        className="App"
        style={{
          backgroundColor: colors.grayBlue,
          color: colors.white,
          fontFamily: "Monaco, monospace",
          minHeight: "100vh",
        }}
      >
        <Helmet>
          <title>Digesticle</title>
        </Helmet>
        <header
          className="App-header"
          style={{
            backgroundColor: colors.grayRed,
            display: "flex",
            alignItems: "center",
            padding: "10px",
            fontFamily: "Verdana",
          }}
        >
          <Link to="/">
            <img src="name_logo.png" alt="Logo" style={{ height: "50px", marginRight: "10px" }} />
          </Link>
          <Link
            style={{
              textDecoration: "none",
              color: "#F0EAD6",
              marginRight: "20px",
            }}
            to="/"
          >
            <div>Stories</div>
          </Link>
          <Link
            style={{
              textDecoration: "none",
              color: "#F0EAD6",
              marginRight: "20px",
            }}
            to="/about"
          >
            <div>About</div>
          </Link>
        </header>
        <Routes>
          <Route exact path="/" element={<StoriesList stories={stories}/>} />
          <Route path="/about" element={about} />
          <Route path="/story/:id" element={<StoryPage />}></Route>
        </Routes>
        <footer>
          <p>&copy; 2025 Digesticle</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
