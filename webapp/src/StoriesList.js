import React from "react";
import { Link } from "react-router-dom";

import { colors } from "./config";

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

export default function StoryItems(props) {
  const stories = props.stories;
  return (
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
                {index === 0 ? (
                  <LeadStoryListItem story={story} />
                ) : (
                  <StoryListItem story={story} />
                )}
              </li>
            ))}
          </ul>
        ) : (
          <div>Loading...</div>
        )}
      </section>
    </main>
  );
}
