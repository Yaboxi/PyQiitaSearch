import csv
import datetime
import json
import os

import requests  # APIを叩く処理をシンプルにするために利用
from tqdm import tqdm  # ページフェッチの進捗を可視化するために利用

API_KEY = "INPUT YOUR KEY"
SEARCH_QUERY = "tag:スクラム"


def get_articles():
    """SEARCH_QUERYでQiitaを検索し、検索結果の記事一覧(articles)をリスト形式で返す
    投稿記事をGETするQiita APIは、全ての記事を一度に返すようにはなっておらず、代わりにページを指定する必要がある
    そのためまず総記事数を取得してから、総ページを算出し、その後各ページの記事を取得する   
    """
    PER_PAGE_MAX = 100  # APIで取得できる1ページの最大記事数
    headers = {"Authorization": "Bearer %s" % (API_KEY)}  # Bearer認証用ヘッダ

    # 検索結果の総記事数を取得する
    total_articles = int(
        requests.get(
            "https://qiita.com/api/v2/items",
            headers=headers,
            params={"query": SEARCH_QUERY},
        ).headers["Total-Count"]
    )
    print("The total count of the articles is :", total_articles)

    # 総ページ数を算出する
    total_pages = total_articles // PER_PAGE_MAX + 1  # 総ページ数 = (総記事数 / 1ページの記事数)の商 + 1

    # 各ページの記事を取得する
    articles = []

    for page in tqdm(range(total_pages)):
        res = requests.get(
            "https://qiita.com/api/v2/items",
            headers=headers,
            params={"page": page + 1, "per_page": PER_PAGE_MAX, "query": SEARCH_QUERY,},
        )  # ページは1からはじまる
        page_articles = json.loads(res.text)

        articles.extend(page_articles)

    return list(articles)


def extract_items(articles):
    """記事一覧から必要な情報のみを抽出し、リスト形式で返す
    抽出するのは title, url, updated date, likes count, tags"""
    extracted_items = []
    for article in articles:
        d = {
            "title": article["title"],
            "url": article["url"],
            "updated_at": article["updated_at"],
            "likes_count": article["likes_count"],
        }

        # タグのみ不定数のため、あるだけ末尾に追加
        for i, tag in enumerate(article["tags"]):
            key = "tag" + str(i)
            d[key] = tag["name"]

        extracted_items.append(d)

    return extracted_items


def write_to_csv(items):
    """リストをCSVに出力する
    アウトプットパスは"Outputs/YYMMDDHHMMSS_検索文字列.csv"
    フォルダOutputsがない場合作成する
    """

    # アウトプットパスの設定
    now = datetime.datetime.now()
    output_dir_path = "Outputs/"
    output_file_path = now.strftime("%y%m%d%H%M%S") + "_" + SEARCH_QUERY + ".csv"

    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)

    # CSVの書き出し
    with open(os.path.join(output_dir_path, output_file_path), "w") as f:
        writer = csv.writer(f)
        for item in items:
            writer.writerow(item.values())
        print("Output CSV is : " + output_dir_path + output_file_path)


if __name__ == "__main__":
    articles = get_articles()
    extracted_items = extract_items(articles)
    write_to_csv(extracted_items)
