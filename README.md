# rakuten_room_goods_arrival_notfication
the app which notifies goods arrivals listed on rakuten pages.

## 環境構築

下記コマンド実行で pipenv installを行ってpython環境を構築する
```
$ docker-compose up -d --build
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
