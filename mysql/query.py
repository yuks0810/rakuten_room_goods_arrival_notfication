import MySQLdb
import datetime

from pyasn1.type.univ import Null


def create_db_connection():
    global conn
    global cur

    conn = MySQLdb.connect(
        user='root',
        passwd='root',
        host='rakuten_db_mysql',
        db='rakute_app_db'
    )
    cur = conn.cursor()
    return conn, cur


def close_db_connections():
    cur.close
    conn.close


def insert_into_products_table(
    latest_notification_date=datetime.datetime.now(),
    rakuten_product_url="",
    rakuten_room_url="",
    affiliate_url=""
):
    db_name = "rakuten_app_db"
    sql = f"INSERT INTO `{db_name}`.`products` \
                    (rakuten_product_url, rakuten_room_url, affiliate_url, latest_notification_date) \
            VALUES  ('{rakuten_product_url}', '{rakuten_room_url}', '{affiliate_url}', '{latest_notification_date}');"
    cur.execute(sql)
    conn.commit()


def update_set_products_table(
    rakuten_product_url,
    latest_notification_date,
    rakuten_room_url=Null,
    affiliate_url=Null
):
    db_name = "rakuten_app_db"
    sql = f'UPDATE `products` \
            SET latest_notification_date = "{latest_notification_date}" \
            WHERE rakuten_product_url = "{rakuten_product_url}";'
    cur.execute(sql)
    conn.commit()


def select_from_products_table(rakuten_product_url):
    db_name = "rakuten_app_db"
    sql = f"SELECT id, latest_notification_date \
            FROM `products` \
            WHERE rakuten_product_url = '{rakuten_product_url}';"
    cur.execute(sql)
    row = cur.fetchone()
    return row
