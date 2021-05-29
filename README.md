# rakuten_room_goods_arrival_notfication
the app which notifies goods arrivals listed on rakuten pages.

## 環境構築
下記コマンド実行で pipenv installを行ってpython環境を構築する
```
$ docker-compose up -d --build
```

### ローカルで作業するとき（log見れない）
スクレイピングを実行
```
$ docker-compose run rakuten python lambda_function.py
```

#### terminalに表示されるlogを見たいとき
```
$ docker-compose exec rakuten bash

# コンテナ内に入った後に下記を実行
$ python lambda_function.py --test_mode
```

## 実行コマンド
### s3に上げるためのコマンド
下記コマンド実行で upload.zipを作成する
```
$ docker-compose exec rakuten sh make_upload.sh
```

### docker環境破壊
作業終了後は下記コマンド実行
```
$ docker-compose down --rmi all --volumes --remove-orphans
```
OR
```
$ docker system prune
```

## PR作成前
静的解析を実行する

<file_name>の箇所に静的解析を行いたいfileの名前(.py)を入力する

```
$ flake8 --config ./setup.cfg --show-source <file_name>

# このような静的解析エラーが出る
lambda_function.py:213:80: E501 line too long (98 > 79 characters)
            msg = '{rand_str}\r\n急ぎの方こちら↓\r\n{rakuten_affiliate_url}\r\n{rakute_room_url}'.format(
                                                                               ^
lambda_function.py:255:31: W291 trailing whitespace
    args = parser.parse_args() 
                              ^
lambda_function.py:258:80: E501 line too long (88 > 79 characters)
    print(lambda_handler(event=None, context=None, test_mode=args.test_mode), type=bool)
```

静的解析で出力されたエラーを自動修正する
このコードで全て修正できるわけではないので、再確認・手動修正も必要な場合あり。

```
$ autopep8 --global-config ./setup.cfg -ivr

# このような修正コードが出る
incorrect number of argumentsroot@10d680bf8aa9:/webapp# autopep8 --global-config ./setup.cfg -ivr lambda_function.py 
[file:lambda_function.py]
--->  Applying global fix for E265
--->  3 issue(s) to fix {'E501': {258, 213}, 'W291': {255}}
--->  1 issue(s) to fix {'E501': {213}}
```
