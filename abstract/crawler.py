from datetime import datetime
import crawler_helper
import db
import helper
import time
import cached


class Crawler:
    def __init__(self, id, start_url, allowed_domains):
        self.id = id
        self.start_url = start_url
        self.count_processed = 0
        self.allowed_domains = allowed_domains

    def log_message(self, s):
        helper.log_message('['+self.id+"]: "+s)

    def fetch_new_urls(self, url):
        bs4_object = crawler_helper.get(url)

        if bs4_object:
            self.url_collector(url, bs4_object)
        else:
            self.log_message(url + " error ")

    def start(self):
        # Fetch Start URL First
        self.fetch_new_urls(self.start_url)

        # Now fetch all link in database
        self.fetch_url_in_db()

    def set_url_invalid(self, id):
        db.query("UPDATE urls SET status = -1 where id = %s", [id])

    def set_url_valid(self, id):
        db.query("UPDATE urls SET status = 1 where id = %s", [id])

    def fetch_url_from_db(self, row):
        row_id = row['id']

        url = row["url"]

        bs4_object = False

        try:

            bs4_object = crawler_helper.get(url)

        except Exception:
            self.set_url_invalid(row_id)

        if bs4_object:
            self.url_collector(url, bs4_object)
            self.set_url_valid(row_id)
        else:
            self.log_message(url + " error ")
            self.set_url_invalid(row_id)

    def fetch_url_in_db(self):
        while True:
            # Loop for each url in db
            rows = db.get_results("SELECT * FROM urls WHERE status !=-1 and status !=1 and source_id=%s order by id desc limit 200",[self.id])
            if len(rows):
                for row in rows:
                    self.fetch_url_from_db(row)
            else:
                self.log_message("No new urls found, sleep 2s")
                time.sleep(1)

    def url_collector(self, origin_url, bs4_object):
        a_tags = bs4_object.findAll('a')
        if len(a_tags) > 0:
            sql = "INSERT IGNORE INTO urls (url,created_at,status,source_id) VALUES "
            insert = []
            format = []

            filtered_urls = []

            for link in a_tags:
                filtered_url = self.filter_url(link.get('href'), self.start_url)
                if filtered_url:
                    filtered_urls.append(filtered_url)

            filtered_urls = list(set(filtered_urls))

            if len(filtered_urls):
                for filtered_url in filtered_urls:
                    insert.extend([filtered_url, datetime.now(), 0, self.id])
                    format.append("(%s,%s,%s,%s)")

                sql += ",".join(format)

                row_count = db.query(sql, insert)

                self.log_message(str(row_count) + " new url(s) inserted.")
                return row_count
            else:
                self.log_message('No new urls found in ')

    def filter_url(self, url, source_url):
        if url in ['#', '/']:
            return False
        if url is None:
            return False

        # Remove Hash from string
        if url.find('#') > -1:
            url = url[0:  url.find('#')]

        if url[0: 2] == '//':
            url = 'http:' + url

        if url[0: 4] != 'http':
            url = source_url + url

        # Check Allowed Domain for outside domain
        # We need to remove query string first,  for example: http://fakedomcain.com?source=my_domain.com
        url_no_query_string = url[0:  url.find('?')]
        url_no_query_string = url_no_query_string[0:  url_no_query_string.find('&')]

        flag_domain = False
        for domain in self.allowed_domains:
            if url_no_query_string.find(domain) > -1:
                flag_domain = True

        if flag_domain is False:
            return False

        # Inserted into Global total_urls
        # print(len(cached.total_urls))
        # if url in cached.total_urls:
        #     print(url," in list")
        #     return False
        # else:
        #     cached.total_urls.append(url)

        # Remove Special str
        search_keys = ['javascript', 'voice', '/u/']

        for key in search_keys:
            if url.find(key) > -1:
                return False

        return url