import scrapy
from scrapy.crawler import CrawlerProcess
from tqdm import tqdm
import logging

# Import from utils
from utils import Article, get_testing_mongodb_collection, clean_text

class TradewindsSpider(scrapy.Spider):
    name = 'marine-link'
    base_url = 'https://www.tradewindsnews.com/archive/?offset={offset}&q={keyword}&publishdate=y'
 
    def __init__(self, *args, **kwargs):
        super(TradewindsSpider, self).__init__(*args, **kwargs)
        self.page_count = 1
        self.keywords = [
            'disruption', 'risk', 'delay', 'congestion', 'accident', 
            'collision', 'piracy', 'hijack', 'terrorism', 'criminal',
            'cargo damage', 'inland', 'environment', 'pollution', 
            'event', 'extreme weather', 'detention', 'regulations', 
            'policy', 'politics'
        ]
        self.articles_count = 0
        self.progress_bar = tqdm(desc="Scraping articles", unit="article", total=self.page_count*len(self.keywords)*10)

        # Setup mongodb connection
        self.collection = get_testing_mongodb_collection()

        # Disable scrapy and mongodb logging
        logging.getLogger('scrapy').setLevel(logging.WARNING)
        logging.getLogger('pymongo').setLevel(logging.WARNING)

    # Start crawling articles using the keywords on first page_count pages
    def start_requests(self):
        # for key in self.keywords:
        #     for i in range(1, self.page_count + 1):
        #         yield scrapy.Request(self.base_url.format(keyword=key, page=i), self.parse)
        url_value = self.base_url.format(keyword="disruption", offset=0) # in increments of 10
        yield scrapy.Request(url_value, self.parse)

    def parse(self, response):
        # Extract article links from the search page
        article_links = response.css('div.col-12 a.card-link.text-reset::attr(href)').getall()

        # Follow each article link
        for link in article_links:
            yield response.follow(link, self.parse_article)

    def parse_article(self, response):
        TEXT_SELECTOR = 'p:not([class])::text'
        TITLE_SELECTOR = 'h1.article-title::text'

        # check if the article is locked behind a paywall
        paywall = response.css("div.sub-paywall-container").extract()
        if len(paywall) != 0:
            self.articles_count += 1
            self.progress_bar.update(1)
            return
        
        text = ' '.join([clean_text(p) for p in response.css(TEXT_SELECTOR).extract()]).strip()
        title = clean_text(response.css(TITLE_SELECTOR).extract_first() or '')

        article = Article(
            headline=title,
            description=text,
            severity="",
            main_risk="",
            country="",
            state="",
            link=response.url
        )

        # Save the article to MongoDB
        self.collection.update_one({"_id": article.link}, {"$set": article.to_dict()}, upsert=True)
        
        self.articles_count += 1
        self.progress_bar.update(1)

        yield article.to_dict()

    def closed(self, reason):
        self.progress_bar.close()
        print(f"\nTotal articles scraped: {self.articles_count}\n")

if __name__ == '__main__':
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    })
    process.crawl(TradewindsSpider)
    process.start()