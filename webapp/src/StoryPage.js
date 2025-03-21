import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { apiHost, colors } from "./config";

function StoryImage(props) {
  const image = props.image;
  if (!image) return <div>No image available</div>;
  const image_url = image.url;
  if (!image_url) return <div>No image URL available</div>;

  return (
    <div style={{ display: "flex", justifyContent: "center", margin: "10px" }}>
        <img src={image_url} alt={image_url} style={{ height: "200px" }} />
    </div>
  );
}

export default function StoryPage() {
  const { id } = useParams();
  const [story, setStory] = useState(null);

  useEffect(() => {
    const fetchStory = async () => {
      const response = await fetch(apiHost + `/story/${id}`);
      const data = await response.json();
      setStory(data);
      console.log(data);
    };
    fetchStory();
  }, [id]);

  const story_items = story ? (
    <ul>
      {story.summary.map((sentence, index) => {
        if (index === 0 && story.images?.length > 0) {
          return [
            <li key={`story-item-${index}`} style={{ marginBottom: "10px" }}>
              {sentence}
            </li>,
            <StoryImage image={story.images[0]} />,
          ];
        }
        if (index === 2 && story.images.length > 1) {
          return [
            <li key={`story-item-${index}`} style={{ marginBottom: "10px" }}>
              {sentence}
            </li>,
            <StoryImage image={story.images[1]} />,
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
        gap: "10px",
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
                src={article.provider.favicon_url}
                alt={article.provider.name}
                style={{ width: "16px", height: "16px", marginRight: "5px" }}
              />
              <p>{article.provider.name}</p>
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
              {article.date}
            </p>
          </div>
          <p style={{ margin: "5px", fontSize: "13px" }}>{article.title}</p>
          <p style={{ margin: "5px", fontSize: "12px", color: colors.lightGray }}>
            {article.subtitle}
          </p>
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
        margin: "10px",
        borderRadius: "10px",
      }}
    >
      <h4 style={{ margin: "0px" }}>Coverage</h4>
      <ul style={{ backgroundColor: "rgba(0, 0, 0, 0.1)", padding: "20px" }}>
        {story.coverage.map((sentence, index) => (
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
        // margin: "20px",
        // backgroundColor: "rgba(0, 0, 0, 0.1)",
      }}
      className="m-[10px] md:m-[40px]"
    >
      <div className="flex flex-col md:flex-row gap-4">
        <div className="md:flex-[2] w-full">
          {story ? (
            <div>
              <h1 className="mb-2 text-2xl font-bold">{story.title}</h1>
              {story_items}
            </div>
          ) : (
            <div className="m-4">Loading...</div>
          )}
        </div>
        <div className="md:flex-[1] w-full">
          {coverage_section}
        </div>
      </div>
      <div>
        <h3>{story.articles.length} Articles</h3>
        {articles_items}
      </div>
    </div>
  ) : (
    <div>Loading...</div>
  );
}
