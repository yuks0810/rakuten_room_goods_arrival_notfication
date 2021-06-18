<img src="https://img.shields.io/badge/-Python-F9DC3E.svg?logo=python&style=flat">
<img src="https://img.shields.io/badge/-Amazon%20AWS-232F3E.svg?logo=amazon-aws&style=flat">

# rakuten_room_goods_arrival_notfication
<img src="https://img.shields.io/badge/ver.-v2.1.0-ff7964.svg?style=for-the-badge">

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
$ python lambda_function.py
```

## 実行コマンド
<img src="https://img.shields.io/badge/kakakakakku-must--check-life-232f3e.svg?style=for-the-badge">



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

## EC2での動かし方
### 対象のインスタンス
Name: rakute_scrayping
インスタンスID: i-0be5be70f0ca22e21
このインスタンスが停止している場合は、インスタンスを起動する。
### EC2にssh接続する

<バブリックIP>の部分はawsの対象のEC2をみて確認
```
# -iのあとのpath指定はrakuten_scrayping_sub.pemがある場所を指定する
$ ssh -i ~/.ssh/rakuten_scrayping_sub.pem ec2-user@<バブリックIP>
```
### sshでEC2に接続したあと

下記のコマンドを実行して、`rakuten_room_goods_arrival_notfication_rakuten`が出てくればアプリが起動しているということ
```
$ docker ps

CONTAINER ID   IMAGE                                            COMMAND                  CREATED        STATUS          PORTS     NAMES
8e78758594a6   rakuten_room_goods_arrival_notfication_rakuten   "/bin/sh -c 'while :…"   26 hours ago   Up 47 seconds             rakuten
```

アプリが起動している場合は、下記を実行
そうすると、スクレイピングが実行される。
```
$ docker-compose exec rakuten bash

# コンテナ内に入った後に下記を実行
$ python lambda_function.py
```

アプリが起動していない場合は

```
$ docker-compose up -d --build
```
を行なってから以下を確認する

```
$ docker ps

CONTAINER ID   IMAGE                                            COMMAND                  CREATED        STATUS          PORTS     NAMES
8e78758594a6   rakuten_room_goods_arrival_notfication_rakuten   "/bin/sh -c 'while :…"   26 hours ago   Up 47 seconds             rakuten
```

## DB

メインのホストコンテナからターミナルで接続するときのコマンド
```
mysql -u root -p -h rakuten_db_mysql -P 3306 --protocol=tcp -D rakute_app_db
```

パスワードは `.env` ファイルに記載されている。

### 接続情報

```
hostname: rakuten_db_mysql
password: .envに記載
user: root
db: rakute_app_db
```

## 過去ログ

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
