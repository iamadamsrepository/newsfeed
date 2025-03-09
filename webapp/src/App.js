import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet';

const colors = {
  red: '#fd5754',
  blue: '#5be1e7',
  white: '#FFFFFF',
  black: '#000000',
  grayRed: '#3d2a33',
  grayBlue: '#2a2c3d'
};

function App() {

  const storyItems = (        
      <main style={{ backgroundColor: colors.grayBlue, display: 'flex', height: '100vh' }}>
          <section style={{ flex: 1, padding: '20px', outline: '1px solid #FFFFFF', margin: '20px' }}>
            <h2>About This Website</h2>
            <p>This website provides the latest news stories from around the world.</p>
          </section>
          <section style={{ flex: 2, padding: '20px', outline: '1px solid #FFFFFF', margin: '20px'}}>
            <h2>News Stories</h2>
            <p>Here are the latest news stories...</p>
          </section>
      </main>
  );

  return (
    <Router>
      <div className="App">
        <Helmet>
          <title>My React App</title>
        </Helmet>
        <header className="App-header" style={{ backgroundColor: colors.grayRed, display: 'flex', alignItems: 'center', padding: '20px', outline: '1px solid #FFFFFF'}}>
          <img src="name_logo.png" alt="Logo" style={{ height: '50px', marginRight: '10px' }} />
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
          <Route path="/about" element={<div>hello</div>} />
          <Route
            path="/story/:id"
            element={<div>hello</div>}
          ></Route>
        </Routes>
        <footer>
          <p>&copy; 2023 My React App</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;