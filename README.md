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
$ docker-compose run rakuten python lambda_function.py --test_mode
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
