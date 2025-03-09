import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

const colors = {
  red: '#fd5754',
  blue: '#5be1e7',
  white: '#FFFFFF',
  black: '#000000',
  grayRed: '#3d2a33',
  grayBlue: '#2a2c3d'
};

function StoryPage() {
  const { id } = useParams();
  const [story, setStory] = useState(null);

  useEffect(() => {
    const fetchStory = async () => {
      const response = await fetch(`http://localhost:8000/story/${id}`);
      const data = await response.json();
      setStory(data);
    };
    fetchStory();
  }, [id]);

  const image_url = story?.image_article?.image_url || "logo.png";
  // console.log("image_url", image_url);

  return (
    <div style={{ display: 'flex', padding: '5px', outline: '0px solid #FFFFFF', margin: '20px', backgroundColor: 'rgba(0, 0, 0, 0.1)' }}>
      <div style={{ flex: 2 }}>
        {story ? (
          <div>
            <h1>{story.title}</h1>
            <ul>
              {story.summary.split('. ').map((sentence, index) => (
                <li key={index}>{sentence}.</li>
              ))}
            </ul>
            <img src={image_url} alt={story.title} />
            <ul style={{ backgroundColor: 'rgba(0, 0, 0, 0.1)', padding: "20px" }}>
              {story.coverage.split('. ').map((sentence, index) => (
                <li key={index}>{sentence}.</li>
              ))}
            </ul>
          </div>
        ) : (
          <div>Loading...</div>
        )}
      </div>
      <div style={{ flex: 1 }}>
        {story && story.articles ? (
          <ul style={{ listStyleType: 'none', padding: 0 }}>
            {story.articles.map((article, index) => (
              <li key={index} style={{ marginBottom: '10px' }}>
                <a href={article.url} target="_blank" rel="noopener noreferrer" style={{ color: colors.blue }}>
                  {article.provider}: {article.title}
                </a>
              </li>
            ))}
          </ul>
        ) : (
          <div>No articles available</div>
        )}
      </div>
    </div>
  );
}

function StoryListItem(props) {
  const story = props.story;
  return (
    <div style={{ display: 'flex', alignItems: 'center', padding: '10px', margin: '10px', backgroundColor: colors.grayBlue, borderRadius: '10px', maxHeight: '200px' }}>
      <Link to={`/story/${story.id}`} style={{ textDecoration: 'none', color: colors.white, display: 'flex', alignItems: 'center', width: '100%' }}>
        {story.image_article ? (
          <img src={story.image_article.image_url} alt={story.title} style={{width: 'auto', maxWidth: '250px', height: 'auto', maxHeight: '200px', borderRadius: '10px', marginRight: '10px'}} />
        ) : (
          <img src="logo.png" alt="logo" style={{ width: 'auto', height: '200px', borderRadius: '10px', marginRight: '10px' }} />
        )}
        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', height: '200px', minHeight: '100%', maxHeight: '100%', position: 'relative' }}>
          <p style={{color: colors.blue, fontSize: "11px", position: 'absolute', top: '0px', left: '0px'}}>From {story.n_articles} Sources</p>
          <h3>{story.title}</h3>
        </div>
      </Link>
    </div>
  );
}

function LeadStoryListItem(props) {
  const story = props.story;
  return (
    <div style={{ display: 'flex', alignItems: 'center', padding: '10px', margin: '10px', backgroundColor: colors.grayRed, borderRadius: '10px', position: 'relative', height: '400px' }}>
      <Link to={`/story/${story.id}`} style={{ textDecoration: 'none', color: colors.white, display: 'flex', alignItems: 'center', width: '100%' }}>
        <p style={{color: colors.blue, fontSize: "11px", position: 'absolute', top: '10px', left: '10px'}}>From {story.n_articles} Sources</p>
        <div>
          <h1 style={{color: colors.red}}>{story.title}</h1>
        </div>
        {story.image_article ? (
          <img src={story.image_article.image_url} alt={story.title} style={{ width: 'auto', maxWidth: '600px', height: 'auto', maxHeight: '400px', borderRadius: '10px', marginRight: '10px' }} />
        ) : (
          <img src="logo.png" alt="logo" style={{ width: 'auto', height: '400px', borderRadius: '10px', marginRight: '10px' }} />
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
        const url = "http://localhost:8000/stories";
        let response = await fetch(url);
        let stories = await response.json();
        stories.forEach(story => {
          story.n_articles = story.articles.length;
        });
        setStories(stories);
        console.log(stories);
      }
    };
    getData();
  }, [stories]);

  const storyItems = (
    <main style={{ backgroundSize: 'cover', backgroundColor: colors.grayBlue, color: colors.white, fontFamily: 'Monaco, monospace', minHeight: '100vh'}}>
      <section style={{ padding: '5px', outline: '0px solid #FFFFFF', margin: '20px', backgroundColor: 'rgba(0, 0, 0, 0.1)'}}>
        <h2>Top Stories</h2>
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
    <div>📰 Only the Most Important Stories, Condensed for You

    AI-Powered Curation 🔥 – We scan thousands of news sources to surface only the most critical breaking stories, so you don’t have to.
    Trusted Journalism 🏆 – No sensationalism, no fluff—just credible news from the world’s most respected outlets.
    Pre-Digested Summaries ✍️ – No more sifting through long articles. Our AI extracts the key facts, context, and takeaways in just a few bullet points.

🌍 The Full Picture, In Seconds

    Multi-Source Perspectives 📡 – See how different outlets report on the same event to get a well-rounded view.
    Bias Awareness 🎭 – Instantly detect political leanings and credibility scores for every story.
    Real-Time Updates ⏳ – Stay ahead with AI-driven tracking of developing news, so you’re always informed.

🔎 Fast. Intelligent. No Noise.

    No clickbait. No distractions.
    No endless scrolling—just what matters.
    News that’s fast, transparent, and to the point.</div>
  )

  return (
    <Router>
      <div className="App" style={{ backgroundColor: colors.grayBlue, color: colors.white, fontFamily: 'Monaco, monospace', minHeight: '100vh' }}>
        <Helmet>
          <title>Digesticle</title>
        </Helmet>
        <header className="App-header" style={{ backgroundColor: colors.grayRed, display: 'flex', alignItems: 'center', padding: '10px', fontFamily: 'Verdana'}}>
          <Link to="/">
            <img src="name_logo.png" alt="Logo" style={{ height: '50px', marginRight: '10px' }} />
          </Link>
          <Link style={{ textDecoration: "none", color: "#F0EAD6", marginRight: '20px' }} to="/">
            <div>Stories</div>
          </Link>
          <Link
            style={{ textDecoration: "none", color: "#F0EAD6", marginRight: '20px' }}
            to="/about"
          >
            <div>About</div>
          </Link>
        </header>
        <Routes>
          <Route exact path="/" element={storyItems} />
          <Route path="/about" element={about} />
          <Route
            path="/story/:id"
            element={<StoryPage/>}
          ></Route>
        </Routes>
        <footer>
          <p>&copy; 2025 Digesticle</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;