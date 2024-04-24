import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useParams } from 'react-router-dom';
import './App.css';
import queryString from 'query-string';

function Input(props) {
  return (
    <div className="flex justify-center">
      <input
        className="flex m-4 p-4 border-black border-4 w-4/5 rounded-[16px] justify-center "
        type="text"
        placeholder="Describe The Movie You Want To See"
        onKeyDown={props.handleKeyDown}
      />
    </div>
  )
}

function MoviePage() {
  const [movie, setMovie] = useState(null)

  useEffect(() => {
    const asyncFn = getData;
    asyncFn();
  });

  const routeParams = useParams()

  const getData = async () => {
    const base_url = 'http://192.168.0.53:8000/movie?'
    const query = queryString.stringify({ i: routeParams["id"]})
    let response = await fetch(base_url + query)
    let json = await response.json()
    setMovie(json)
  }

  if (movie)
    return <div style={{ "height": "800px", "white-space": "normal" }}>
      <img alt="poster" src={movie["image"]} style={{ "height": "300px", "margin-left": "auto", "margin-right": "auto" }}></img>
      <div style={{ "text-align": "center", "font-size": "18px", "margin-left": "10px", "margin-right": "10px", "marginBottom": "6px" }}>{movie.title}</div>
      <div style={{ "display": "flex", "justifyContent": "space-between", "marginBottom": "6px", "font-size": "12px"}}>
        <div></div>
        <div>{Math.floor(movie.runtime/60) + "h" + movie.runtime%60 + "m"}</div>
        <div>&#x2022;</div>
        <div>{movie.content_rating}</div>
        <div>&#x2022;</div>
        <div>{movie.year}</div>
        <div></div>
      </div>
      <div style={{ "display": "flex", "justifyContent": "space-between", "marginBottom": "6px", "font-size": "14px" }}>
        <div></div>
        <div>
          <img alt="metacritic" src="https://www.metacritic.com/favicon.ico" style={{ "height": "22px", "display": "inline-block"}}></img>
          <div style={{ "display": "inline-block", "marginLeft": "8px" }}>{movie.metascore}</div>
        </div>
        <div>
          <img alt="imdb" src="https://m.media-amazon.com/images/G/01/imdb/images-ANDW73HA/favicon_desktop_32x32._CB1582158068_.png" style={{ "height": "22px", "display": "inline-block"}}></img>
          <div style={{ "display": "inline-block", "marginLeft": "8px" }}>{movie.rating}</div>
        </div>
        <div></div>
      </div>
      <div style={{ }}>
        {
          movie.genres.map(genre => (
            <div style={{ "display": "inline-block", }} className="m-1 p-1 bg-slate-500 rounded-lg text-sm text-white">{genre}</div>
          ))
        }
      </div>
    </div>
  else
    return <div></div>
}

function MovieItemDisplay(props) {
  var className = "m-1 p-1 rounded-xl hover:outline hover:outline-slate-500 hover:outline-2"
  const movie = props.movie["movie"]

  return <div style={{ "height": "500px", "white-space": "normal" }} className={className}>
    <img alt="poster" src={movie["image"]} style={{ "height": "300px", "margin-left": "auto", "margin-right": "auto" }}></img>
    <div style={{ "text-align": "center", "font-size": "18px", "margin-left": "10px", "margin-right": "10px", "marginBottom": "6px" }}>{movie.title}</div>
    <div style={{ "display": "flex", "justifyContent": "space-between", "marginBottom": "6px", "font-size": "12px"}}>
      <div></div>
      <div>{Math.floor(movie.runtime/60) + "h" + movie.runtime%60 + "m"}</div>
      <div>&#x2022;</div>
      <div>{movie.content_rating}</div>
      <div>&#x2022;</div>
      <div>{movie.year}</div>
      <div></div>
    </div>
    <div style={{ "display": "flex", "justifyContent": "space-between", "marginBottom": "6px", "font-size": "14px" }}>
      <div></div>
      <div>
        <img alt="metacritic" src="https://www.metacritic.com/favicon.ico" style={{ "height": "22px", "display": "inline-block"}}></img>
        <div style={{ "display": "inline-block", "marginLeft": "8px" }}>{movie.metascore}</div>
      </div>
      <div>
        <img alt="imdb" src="https://m.media-amazon.com/images/G/01/imdb/images-ANDW73HA/favicon_desktop_32x32._CB1582158068_.png" style={{ "height": "22px", "display": "inline-block"}}></img>
        <div style={{ "display": "inline-block", "marginLeft": "8px" }}>{movie.rating}</div>
      </div>
      <div></div>
    </div>
    <div style={{ }}>
      {
        movie.genres.map(genre => (
          <div style={{ "display": "inline-block", }} className="m-1 p-1 bg-slate-500 rounded-lg text-sm text-white">{genre}</div>
        ))
      }
    </div>
  </div>
}

function MovieDisplay(props) {
  const width = { 1: "100%", 2: "50%", 3: "33.3%", 4: "25%" }
  const tdStyle = { "width": width[props.columns], "overflow": "hidden" }
  const cols = props.columns
  const rows = Math.ceil(props.movies.length / cols)

  var movieGrid = []
  for (let i = 0; i < rows; i++)
    movieGrid.push(props.movies.slice(i * cols, cols * (i + 1)))

  return <div className="">
    <table style={{ "width": "100%", "tableLayout": "fixed" }}>
      <tbody>
        {
          movieGrid.map(movieRow => (
            <tr>
              {movieRow.map(movie => (
                <td style={tdStyle} >
                  <MovieItemDisplay movie={{ movie }} />
                </td>
              ))}
            </tr>
          ))
        }
      </tbody>
    </table>
  </div>
}

function Body(props) {
  var className = " min-h-screen "
  if (props.screenSize.width < 1000) {
    className += "min-w-full max-w-full "
  } else {
    className += "min-w-[1000px] max-w-[1000px] w-[1000px]"
  }

  var columns
  if (props.screenSize.width > 840) {
    columns = 4
  } else if (props.screenSize.width > 560) {
    columns = 3
  } else if (props.screenSize.width > 280) {
    columns = 2
  } else {
    columns = 1
  }

  var columnWidth
  if (props.screenSize.width > 1000) {
    columnWidth = 250
  } else {
    columnWidth = Math.ceil(props.screenSize.width / columns)
  }
  columnWidth = 250

  return <div className={className}>
    <div className="flex justify-center">
      <h1 className="m-4 text-3xl font-mono">
        Natural Language to Movie Recommendations
      </h1>
    </div>
    <Router>
      <Routes>
        <Route exact path="/" element={
          <div>
            <Input handleKeyDown={props.handleKeyDown.bind(this)} />
            <MovieDisplay movies={props.movies} columnWidth={columnWidth} columns={columns} />
          </div>
        }/>
        <Route path="/movie/:id" element={<MoviePage />}/>
      </Routes>
    </Router>
  </div>

}


export default function App() {
  const [movies, setMovies] = useState([]);
  const [screenSize, setScreenSize] = useState(getCurrentDimension());

  function getCurrentDimension() {
    return {
      width: window.innerWidth,
      height: window.innerHeight
    }
  }

  useEffect(() => {
    const updateDimension = () => {
      setScreenSize(getCurrentDimension())
    }
    window.addEventListener('resize', updateDimension);

    return (() => {
      window.removeEventListener('resize', updateDimension);
    })
  }, [screenSize])

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      const base_url = 'http://192.168.0.53:8000/?'
      const query = queryString.stringify({ sentence: event.target.value })
      fetch(base_url + query)
        .then(response => response.json())
        .then(data => setMovies(data))
    }
  }

  return (
    <div className="bg-teal-100 flex justify-center">
      <Body handleKeyDown={handleKeyDown.bind(this)} movies={movies} screenSize={screenSize} />
    </div>)
}
