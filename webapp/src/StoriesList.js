import React from "react";
import { Link } from "react-router-dom";

import { colors } from "./config";


function StoryListItem(props) {
  const story = props.story;
  return (
    <Link to={`/story/${story.id}`} className="flex flex-row m-2">
      {story?.images?.length > 0 ? (
        <div className="flex-[1] w-full p-1">
          <img
            className="rounded-[2vw]"
            src={story.images[0].url}
            alt={story.title}
          />
        </div>

      ) : (
        <img
          src="logo.png"
          alt="logo"
        />
      )}
      <div className="flex-[1] md:flex-[2] w-full ml-0 mt-0 md:ml-6 md:mt-6">
        <div className="text-[9px] md:text-[10px] text-myblue">From {story.n_articles} Sources</div>
        <div className="text-sm h-full place-content-center pb-10">
          <div>{story.title}</div>
        </div>
      </div>
    </Link>
  )
}

function LeadStoryListItem(props) {
  const story = props.story;
  return (
    <div className="bg-mydarkRed p-3 rounded-[2vw]">
      <div className="pb-2 text-[20px] md:text-[30px]">Top Story</div>
      <Link to={`/story/${story.id}`} className="flex flex-col md:flex-row">
        <div className="md:flex-[1] w-full">
          <div className="text-[9px] md:text-[10px] text-myblue">From {story.n_articles} Sources</div>
          <div className="h-full place-content-center">
            <div>{story.title}</div>
          </div>
        </div>
        {story?.images?.length > 0 ? (
          <img
            className="md:flex-[1] w-full rounded-[2vw]"
            src={story.images[0].url}
            alt={story.title}
          />
        ) : (
          <img
            src="logo.png"
            alt="logo"
          />
        )}
      </Link>
    </div>
  )
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
        }}
        className="m-[10px] md:m-[40px]"
      >
        <div className="text-[30px] md:text-[40px] mb-2 md:mb-6">Daily Digest</div>
        {stories.length > 0 ? (
          <ul style={{ listStyleType: "none", padding: 0, margin: 0 }}>
            {stories.map((story, index) => (
              <li key={index}>
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
