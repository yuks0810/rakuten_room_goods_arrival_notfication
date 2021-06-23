import MySQLdb
import datetime
import os

from pyasn1.type.univ import Null


def create_db_connection():
    global conn
    global cur

    conn = MySQLdb.connect(
        user=os.environ['MYSQL_USER'],
        passwd=os.environ['MYSQL_ROOT_PASSWORD'],
        host=os.environ['MYSQL_HOST'],
        db=os.environ['MYSQL_DATABASE']
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
            VALUES  ('{rakuten_product_url}', '{rakuten_room_url}', '{affiliate_url}', '{latest_notification_date}')"
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
            WHERE rakuten_product_url = "{rakuten_product_url}"'
    cur.execute(sql)
    conn.commit()


def select_from_products_table(rakuten_product_url):
    db_name = "rakuten_app_db"
    sql = f"SELECT id, latest_notification_date \
            FROM `products` \
            WHERE rakuten_product_url = '{rakuten_product_url}'"
    cur.execute(sql)
    row = cur.fetchone()
    return row


def create_products_tabl(table_name):
    db_name = "rakuten_app_db"
    drop_table_sql = f"DROP TABLE IF EXISTS {table_name};"
    create_table_sql = f"CREATE TABLE {table_name}( \
                        id INT(11) PRIMARY KEY AUTO_INCREMENT, \
                        rakuten_product_url VARCHAR(255), \
                        rakuten_room_url VARCHAR(255), \
                        affiliate_url VARCHAR(255), \
                        latest_notification_date DATETIME);"
    try:
        cur.execute(drop_table_sql)
        cur.execute(create_table_sql)

    except Exception as e:
        print(e)
    
    close_db_connections()


def create_database():
    sql = "CREATE DATABASE IF NOT EXISTS rakuten_app_db"


if __name__ == "__main__":
    conn, cur = create_db_connection()
    # productsテーブルを作成
    create_products_tabl("products")
