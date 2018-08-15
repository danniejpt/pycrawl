from bs4 import BeautifulSoup
import requests
from datetime import datetime
import mysql.connector

db_connector = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="pycrawl"
)

db = db_connector.cursor()

url_status = {
    0:"Initial Status",
    1:"Valid URL",
    -1:"Invalid URL",
}

def get(url):
    request = requests.get(url)

    if (request.status_code != 200): return None

    plain = request.text
    s = BeautifulSoup(plain, 'html.parser')
    return s


def log_error(s):
    print(datetime.now(), ": ", s)


def url_collector(origin_url, bs4_object):
    a_tags = bs4_object.findAll('a')
    if len(a_tags) > 0:
        sql = "INSERT INTO urls (url,source,created_at,status) VALUES "
        insert = []
        format = []

        for link in a_tags:
            insert.extend([link.get('href'), origin_url, datetime.now(), 0])
            format.append("(%s,%s,%s,%s)")

        sql += ",".join(format)
        db.execute(sql, insert)
        db_connector.commit()

        log_error(str(db.rowcount) + " url(s) record inserted.")

# def crawl_url(row):


urls = ["http://www.nettruyen.com/", "http://truyentranhtam.com/"]

for url in urls:
    bs4_object = get(url)
    if (bs4_object is None):

        print(log_error(url + " error "))

    else:
        try:
            url_collector(url, bs4_object)
        except Exception as e:
            log_error(e)

while True:
    # Loop for each url in db
    db.execute("SELECT * FROM urls WHERE status !=-1 order by id desc limit 200")
    # for row in db.fetchall():

