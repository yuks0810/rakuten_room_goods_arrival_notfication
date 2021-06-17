import MySQLdb
import datetime

def insert_into_products_table(cur, latest_notification_date, rakuten_product_url="", rakuten_room_url="", affiliate_url=""):
    sql = "INSERT INTO `rakute_app_db`.`products` \
                (rakuten_product_url, rakuten_room_url, affiliate_url, latest_notification_date) \
        VALUES  ('{rakuten_product_url}', '{rakuten_room_url}', '{affiliate_url}', '{latest_notification_date}');".format(
        rakuten_product_url=rakuten_product_url,
        rakuten_room_url=rakuten_room_url,
        affiliate_url=affiliate_url,
        latest_notification_date=latest_notification_date
    )
    cur.execute(sql)
    conn.commit()

if __name__ == "__main__":
    # 接続する
    conn = MySQLdb.connect(
        user='root',
        passwd='root',
        host='rakuten_db_mysql',
        db='rakute_app_db'
    )
    cur = conn.cursor()

    insert_into_products_table(cur, datetime.datetime.now())

    rows = cur.fetchall()
    for row in rows:
        print(row)

    cur.close
    conn.close
