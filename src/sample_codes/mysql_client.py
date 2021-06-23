import MySQLdb
import datetime

def insert_into_products_table(cur, latest_notification_date, rakuten_product_url="", rakuten_room_url="", affiliate_url=""):
    sql = "INSERT INTO `rakuten_app_db`.`products` \
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
        db='rakuten_app_db'
    )
    cur = conn.cursor()

    # insert_into_products_table(
    #     cur,
    #     datetime.datetime.now(),
    #     rakuten_product_url="https://books.rakuten.co.jp/rb/14647228/?l-id=search-c-item-img-03",
    #     rakuten_room_url="https://room.rakuten.co.jp/room_shin_/1700119686145260",
    #     affiliate_url="https://a.r10.to/hy57jq"
    # )

    sql = "select id, latest_notification_date from products where rakuten_product_url = 'https://books.rakuten.co.jp/rb/14647228/?l-id=search-c-item-img-03'"
    cur.execute(sql)

    rows = cur.fetchall()
    print(len(rows))
    for row in rows:
        print(row[1])

    cur.close
    conn.close
