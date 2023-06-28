import argparse
import csv
import datetime
import json
import os

import requests
from dotenv import load_dotenv
from tqdm import tqdm


class QiitaArticleFetcher:
    def __init__(self, api_key, query):
        self.api_key = api_key
        self.query = query
        self.headers = {"Authorization": "Bearer %s" % api_key}

    def fetch_articles(self):
        max_articles_per_page = 100

        total_article_count = int(
            requests.get(
                "https://qiita.com/api/v2/items",
                headers=self.headers,
                params={"query": self.query},
            ).headers["Total-Count"]
        )

        print("Total number of articles :", total_article_count)

        total_page_count = total_article_count // max_articles_per_page + 1

        all_articles = []
        for page in tqdm(range(total_page_count)):
            response = requests.get(
                "https://qiita.com/api/v2/items",
                headers=self.headers,
                params={
                    "page": page + 1,
                    "per_page": max_articles_per_page,
                    "query": self.query,
                },
            )
            articles_on_page = json.loads(response.text)
            all_articles.extend(articles_on_page)

        return all_articles

    @staticmethod
    def format_article_data(articles):
        formatted_articles = []
        for article in articles:
            article_data = {
                "title": article["title"],
                "url": article["url"],
                "updated_at": article["updated_at"],
                "likes_count": article["likes_count"],
            }

            for i, tag in enumerate(article["tags"]):
                key = "tag" + str(i)
                article_data[key] = tag["name"]

            formatted_articles.append(article_data)

        return formatted_articles

    def save_articles_to_csv(self, articles):
        current_time = datetime.datetime.now()
        output_dir = "outputs/"
        output_filename = (
            current_time.strftime("%y%m%d%H%M%S") + "_" + str(self.query) + ".csv"
        )

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(os.path.join(output_dir, output_filename), "w") as output_file:
            writer = csv.writer(output_file)
            for article in articles:
                writer.writerow(article.values())

        print("CSV file saved to : " + output_dir + output_filename)


if __name__ == "__main__":
    load_dotenv(verbose=True)

    parser = argparse.ArgumentParser()
    parser.add_argument("--query", help="search query for Qiita articles")
    args = parser.parse_args()

    qiita_api_key = os.environ.get("QIITA_API_KEY")
    fetcher = QiitaArticleFetcher(qiita_api_key, args.query)

    fetched_articles = fetcher.fetch_articles()
    formatted_articles = fetcher.format_article_data(fetched_articles)
    fetcher.save_articles_to_csv(formatted_articles)
