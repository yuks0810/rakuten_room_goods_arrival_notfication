import tweepy

CK = "9MDpJf7SMPDcAFhfaSlqKJY8O" # API_key
CS = "o0E9gm2crpplY3zI78UoIhCl0xaUixmAQdfyaMaEcklJ8RSNEv" # API_secret_key
AT = "1338624287565959168-ZbxjrgPSeVavPFof9oi3u885S4Ajte"
ATS = "EshBkpWPMwuxIU5heIS5mgl2NeqoGSaJfb2nXjjMOWcNI"

# Twitterオブジェクトの生成
auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, ATS)
api = tweepy.API(auth)

# キーボード入力の取得
tweet = input('>> ')

# ツイート
api.update_status(tweet)
