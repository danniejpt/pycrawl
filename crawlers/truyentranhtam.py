from abstract.crawler import Crawler
import db
import time
import crawler_helper

class Truyentranhtam(Crawler):
    def __init__(self):
        super().__init__('tt8', 'http://truyentranh8.org/', ['truyentranh8.org', 'truyentranh8.net'])

    def process_urls(self):
        # Loop for each url in db
        rows = db.get_results("SELECT * FROM urls WHERE status !=-1 and status !=1 and source_id=%s order by id desc limit 200", [self.id])
        if len(rows):
            for row in rows:
                self.process_single_url(row)
        else:
            self.log_message("No new urls found, sleep 2s")
            time.sleep(1)

    def get_url_type(self,bs4_object):
        if len(bs4_object.find('.mangaDescription'))>0:
            return "comic"

        if len(bs4_object.find('.xemtruyen')) > 0:
            return "chapter"

    def process_chapter(self,bs4_object, row):
        print('xx')

    def process_comic(self,bs4_object,row):
        print('s')

    def process_single_row(self,row):
        url = row['url']

        try:
            bs4_object = crawler_helper.get(url)

            type = self.get_url_type(bs4_object)

            if type =='comic':
                self.process_comic(bs4_object,row)


        except Exception:
            self.log_message(url+" error")
            self.set_url_invalid(row["id"])

