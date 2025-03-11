import React from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import { Helmet } from "react-helmet";
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

const apiHost = "http://192.168.1.106:8000";

const colors = {
  red: "#fd5754",
  blue: "#5be1e7",
  white: "#FFFFFF",
  lightGray: "#CCCCCC",
  black: "#000000",
  grayRed: "#3d2a33",
  grayBlue: "#2a2c3d",
};

function breakIntoSentences(text) {
  text = text.replace("U.S.", "US");
  return text.match(/[^.!?]+[.!?]+/g) || [];
}

function formatDate(timestamp) {
  const date = new Date(timestamp);
  return date.toLocaleString("en-GB", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function StoryPage() {
  const { id } = useParams();
  const [story, setStory] = useState(null);

  useEffect(() => {
    const fetchStory = async () => {
      const response = await fetch(apiHost + `/story/${id}`);
      const data = await response.json();
      setStory(data);
    };
    fetchStory();
  }, [id]);

  const image_url = story?.image_article?.image_url || "logo.png";

  const story_items = story ? (
    <ul>
      {breakIntoSentences(story.summary).map((sentence, index) => {
        if (index === 0) {
          return [
            <li key={`story-item-${index}`} style={{ marginBottom: "10px" }}>
              {sentence}
            </li>,
            <div key={`image-${index}`} style={{ display: "flex", justifyContent: "center" }}>
              <img src={image_url} alt={story.title} style={{ height: "200px", margin: "10px" }} />
            </div>,
          ];
        }
        return (
          <li key={`story-item-${index}`} style={{ marginBottom: "10px" }}>
            {sentence}
          </li>
        );
      })}
    </ul>
  ) : (
    <div>Loading...</div>
  );

  const articles_items = story?.articles ? (
    <ul
      style={{
        listStyleType: "none",
        padding: 0,
        display: "grid",
        gridTemplateColumns: window.innerWidth > 800 ? "1fr 1fr" : "1fr",
        gap: "10px"
      }}
    >
      {story.articles.map((article, index) => (
        <li
          key={index}
          style={{
            marginBottom: "15px",
            backgroundColor: "rgba(0, 0, 0, 0.1)",
            padding: "10px",
            borderRadius: "10px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center" }}>
            <a
              style={{
                display: "flex",
                alignItems: "center",
                backgroundColor: colors.grayRed,
                borderRadius: "20px",
                width: "fit-content",
                fontSize: "10px",
                padding: "0px 20px 0px 20px",
                fontWeight: "bold",
                color: colors.blue,
                textDecoration: "none",
              }}
              href={article.provider_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              <img
                src={article.provider_favicon}
                alt={article.provider}
                style={{ width: "16px", height: "16px", marginRight: "5px" }}
              />
              <p>{article.provider}</p>
            </a>
            <a
              style={{
                display: "flex",
                alignItems: "center",
                borderRadius: "20px",
                width: "fit-content",
                fontSize: "10px",
                padding: "0px 20px 0px 20px",
                fontWeight: "bold",
                color: colors.red,
                textDecoration: "none",
                margin: "10px",
                outline: `1px solid ${colors.red}`,
              }}
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              <p>Read Article</p>
            </a>
            <p
              style={{
                margin: "5px",
                fontSize: "12px",
                color: colors.lightGray,
              }}
            >
              {formatDate(article.ts)}
            </p>
          </div>
          <p style={{ margin: "5px", fontSize: "13px" }}>{article.title}</p>
          <p style={{ margin: "5px", fontSize: "12px", color: colors.lightGray }}>{article.subtitle}</p>
        </li>
      ))}
    </ul>
  ) : (
    <div>No articles available</div>
  );

  const coverage_section = story?.coverage ? (
    <div
      style={{
        backgroundColor: colors.grayRed,
        padding: "10px",
        borderRadius: "10px",
      }}
    >
      <h4>Coverage</h4>
      <ul style={{ backgroundColor: "rgba(0, 0, 0, 0.1)", padding: "20px" }}>
        {breakIntoSentences(story.coverage).map((sentence, index) => (
          <li key={index} style={{ marginBottom: "10px", fontSize: "13px" }}>
            {sentence}
          </li>
        ))}
      </ul>
    </div>
  ) : (
    <div></div>
  );

  return story ? (
    <div
      style={{
        padding: "5px",
        outline: "0px solid #FFFFFF",
        margin: "20px",
        backgroundColor: "rgba(0, 0, 0, 0.1)",
      }}
    >
      <div style={{ display: "flex" }}>
        <div style={{ flex: 2 }}>
          {story ? (
            <div>
              <h1 style={{ margin: "10px" }}>{story.title}</h1>
              {story_items}
            </div>
          ) : (
            <div>Loading...</div>
          )}
        </div>
        <div style={{ flex: 1 }}>{coverage_section}</div>
      </div>
      <div>
        <h3>{story.articles.length} Articles</h3>
        {articles_items}
      </div>
    </div>
  ) : (<div>Loading...</div>)
}

function StoryListItem(props) {
  const story = props.story;
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        padding: "10px",
        margin: "10px",
        backgroundColor: colors.grayBlue,
        borderRadius: "10px",
        maxHeight: "200px",
      }}
    >
      <Link
        to={`/story/${story.id}`}
        style={{
          textDecoration: "none",
          color: colors.white,
          display: "flex",
          alignItems: "center",
          width: "100%",
        }}
      >
        {story.image_article ? (
          <img
            src={story.image_article.image_url}
            alt={story.title}
            style={{
              width: "auto",
              maxWidth: "250px",
              height: "auto",
              maxHeight: "200px",
              borderRadius: "10px",
              marginRight: "10px",
            }}
          />
        ) : (
          <img
            src="logo.png"
            alt="logo"
            style={{
              width: "auto",
              height: "200px",
              borderRadius: "10px",
              marginRight: "10px",
            }}
          />
        )}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            height: "200px",
            minHeight: "100%",
            maxHeight: "100%",
            position: "relative",
          }}
        >
          <p
            style={{
              color: colors.blue,
              fontSize: "11px",
              position: "absolute",
              top: "0px",
              left: "0px",
            }}
          >
            From {story.n_articles} Sources
          </p>
          <h3>{story.title}</h3>
        </div>
      </Link>
    </div>
  );
}

function LeadStoryListItem(props) {
  const story = props.story;
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        padding: "10px",
        margin: "10px",
        backgroundColor: colors.grayRed,
        borderRadius: "10px",
        position: "relative",
        height: "400px",
      }}
    >
      <Link
        to={`/story/${story.id}`}
        style={{
          textDecoration: "none",
          color: colors.white,
          display: "flex",
          alignItems: "center",
          width: "100%",
        }}
      >
        <p
          style={{
            color: colors.blue,
            fontSize: "11px",
            position: "absolute",
            top: "10px",
            left: "10px",
          }}
        >
          From {story.n_articles} Sources
        </p>
        <div>
          <h1 style={{ color: colors.red }}>{story.title}</h1>
        </div>
        {story.image_article ? (
          <img
            src={story.image_article.image_url}
            alt={story.title}
            style={{
              width: "auto",
              maxWidth: "600px",
              height: "auto",
              maxHeight: "400px",
              borderRadius: "10px",
              marginRight: "10px",
            }}
          />
        ) : (
          <img
            src="logo.png"
            alt="logo"
            style={{
              width: "auto",
              height: "400px",
              borderRadius: "10px",
              marginRight: "10px",
            }}
          />
        )}
      </Link>
    </div>
  );
}

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

  const storyItems = (
    <main
      style={{
        backgroundSize: "cover",
        backgroundColor: colors.grayBlue,
        color: colors.white,
        fontFamily: "Monaco, monospace",
        minHeight: "100vh",
      }}
    >
      <section
        style={{
          padding: "5px",
          outline: "0px solid #FFFFFF",
          margin: "20px",
          backgroundColor: "rgba(0, 0, 0, 0.1)",
        }}
      >
        <h2>Daily Digest</h2>
        {stories.length > 0 ? (
          <ul style={{ listStyleType: "none", padding: 0, margin: 0 }}>
            {stories.map((story, index) => (
              <li key={story.id}>
                {index === 0 ? <LeadStoryListItem story={story} /> : <StoryListItem story={story} />}
              </li>
            ))}
          </ul>
        ) : (
          <div>Loading...</div>
        )}
      </section>
    </main>
  );

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
          <Route exact path="/" element={storyItems} />
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
