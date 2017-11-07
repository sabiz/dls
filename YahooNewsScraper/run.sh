#scrapy runspider yahoo_news_spider.py -o news.json
scrapy crawl yahoo_news_spider -o ./news/news-`date +%Y%m%d%H%M`.json
