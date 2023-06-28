# py-qiita-search

Qiita API を利用して、指定したクエリに対する検索結果の一覧を CSV に出力します。

## Usage

- Qiita API キーは環境変数を介して設定します。`.env`内に記載してください。
- クエリはコマンドライン引数を通して設定します。以下がその例です。

```shell
python main.py --query "tag:スクラム"
```

- クエリは[Qiita 公式: 検索時に利用できるオプション
  ](https://help.qiita.com/ja/articles/qiita-search-options)を参考に記述してください。

## Author

Yaboxi
