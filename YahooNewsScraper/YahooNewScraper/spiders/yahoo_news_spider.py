# -*- coding: utf-8 -*-

import scrapy


class YahooNewsSpider(scrapy.Spider):
    name = 'yahoo_news_spider'

    start_urls = ['https://news.yahoo.co.jp/flash']

    def parse(self, response):
        for href in response.css('p.ttl > a::attr(href)'):
            full_url = response.urljoin(href.extract())
            # print(full_url)
            yield scrapy.Request(full_url, callback=self.parse_item)

    def parse_item(self, response):
        contents = []
        for content in response.css('p.ynDetailText::text'):
            contents.append(content.extract())
            # print(content.extract())
        if(len(contents) <= 0):
            return #Video news
        yield {
            'title': response.css('div.hd > h1::text').extract(),
            'paragraphs': contents,
        }


