import scrapy
from ..items import SocialbladeTwitter2Item
from datetime import datetime
from config.models import CollectTargetItem
from django.db.models import Q
from crawler.tasks import crawlinglogger

SOCIALBLADE_DOMAIN = "socialblade.com"
SOCIALBLADE_ROBOT = "https://socialblade.com/robots.txt"


class Twitter2Spider(scrapy.Spider):
    name = "twitter2"
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "crawler.scrapy_app.middlewares.NoLoginDownloaderMiddleware": 100
        },
    }

    def start_requests(self):
        for target in self.crawl_target:
            artist_name = target['artist_name']
            artist_url = target['target_url']
            target_id = target['id']
            print("artist : {}, url : {}, url_len: {}".format(
                artist_name, artist_url, len(artist_url)))
            yield scrapy.Request(url=artist_url, callback=self.parse, encoding="utf-8", meta={"artist": artist_name,
                                                                                              "target_id": target_id})

    def parse(self, response):
        if response.request.url == SOCIALBLADE_ROBOT:
            pass
        else:
            artist = response.request.meta["artist"]
            followers_xpath = CollectTargetItem.objects.get(
                Q(collect_target_id=response.meta["target_id"]) & Q(target_name="followers")).xpath + "/text()"
            twits_xpath = CollectTargetItem.objects.get(
                Q(collect_target_id=response.meta["target_id"]) & Q(target_name="twits")).xpath + "/text()"
            user_created_xpath = CollectTargetItem.objects.get(
                Q(collect_target_id=response.meta["target_id"]) & Q(target_name="user_created")).xpath + "/text()"
            try:
                followers = response.xpath(followers_xpath).get()
            except ValueError:
                crawlinglogger.error(f"[400], {artist}, twitter, {followers_xpath}")
            try:
                twits = response.xpath(twits_xpath).get()
            except ValueError:
                crawlinglogger.error(f"[400], {artist}, twitter, {twits_xpath}")
            try:
                user_created = response.xpath(user_created_xpath).get()
            except ValueError:
                crawlinglogger.error(f"[400], {artist}, twitter, {user_created_xpath}")
                # Xpath Error?????? ?????? ??????, ????????? Xpath ???????????? ?????? ???????????????.
            
            if twits is None:
                crawlinglogger.error(f"[400], {artist}, twitter, {twits_xpath}")
            elif followers is None:
                crawlinglogger.error(f"[400], {artist}, twitter, {followers_xpath}")
            elif user_created is None:
                crawlinglogger.error(f"[400], {artist}, twitter, {user_created_xpath}")
                # Xpath??? ???????????? ?????? ??????????????? element??? ?????? ??? ?????? ???????????????.
                # ??????, Xpath?????? ????????? ????????? ?????? ???????????? Element??? ?????? ???????????????.
                # ????????? ?????? item??? yield ?????? ????????? ?????????.
            else:
                item = SocialbladeTwitter2Item()
                item["artist"] = artist
                item["followers"] = followers.replace(",", "")
                item["twits"] = twits.replace(",", "")
                item["user_created"] = user_created
                item["url"] = response.url
                item["reserved_date"] = datetime.now().date()
                yield item
