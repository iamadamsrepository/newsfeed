import json

from googleapiclient.discovery import Resource, build

from db.db_connection import DBHandler


class ImageGuy:
    def __init__(self, db: DBHandler, g_key: str, g_id: str):
        self._db = db
        self._g_key = g_key
        self._g_id = g_id

    def _get_stories_without_images(self) -> list[dict]:
        latest_digest_id = self._db.run_sql(
            """
            select max(digest_id)
            from stories
            """
        )[0][0]
        stories = [
            {"id": i[0], "title": i[1]}
            for i in self._db.run_sql(
                """
            select s.id, s.title
            from stories s
            where s.id not in (select story_id from images)
            and s.digest_id = %s
            """,
                (latest_digest_id,),
            )
        ]
        return stories

    def _google_custom_image_search(self, query, num_images=5):
        service: Resource = build("customsearch", "v1", developerKey=self._g_key)
        res: dict = (
            service.cse()
            .list(q=query, cx=self._g_id, searchType="image", num=num_images, rights="cc_atriubte")
            .execute()
        )

        images: list[dict[str, dict]] = res.get("items", [])
        results = []
        for img in images:
            image_info = {
                "title": img.get("title"),
                "url": img.get("link"),
                "source_page": img.get("image", {}).get("contextLink"),
                "height": img.get("image", {}).get("height"),
                "width": img.get("image", {}).get("width"),
                "format": img.get("mime"),
            }
            results.append(image_info)
        return results

    def _collect_images(self):
        stories = self._get_stories_without_images()
        print(f"Collectings images for {len(stories)} stories")
        for i, story in enumerate(stories):
            print(i, end="\r")
            images = self._google_custom_image_search(story["title"])
            for img in images:
                self._db.insert_row("images", {"story_id": story["id"], **img})


if __name__ == "__main__":
    config = json.load(open("config.json"))
    db_config = config["pi"]
    db = DBHandler(db_config)
    g_key = config["google_search_key"]
    g_id = config["google_search_engine_id"]
    ig = ImageGuy(db, g_key, g_id)
    ig._collect_images()
