import requests


class GetArticle:
    def __init__(self):
        pass

    def save(self, url):
        # TODO: Store data in db
        # TODO: Add celery
        # TODO: Move url to settings/env variables
        # TODO: Error handling
        # TODO: Caching
        # TODO: Store RAW HTML

        article_data = requests.get("http://localhost:3000", data={"url": url})
        if article_data.status_code == 200:
            return article_data.json()

