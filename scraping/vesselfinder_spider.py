import scrapy
from scrapy.crawler import CrawlerProcess
from tqdm import tqdm
import logging

# Import from utils
from utils import Article, get_mongodb_collection, get_testing_mongodb_collection, clean_text

class VesselfinderSpider(scrapy.Spider):
    name = 'marine-link'
    base_url = 'https://www.vesselfinder.com/news?page={page}&category={category}' # category 1 to 6
 
    def __init__(self, *args, **kwargs):
        super(VesselfinderSpider, self).__init__(*args, **kwargs)
        self.page_count = 1
        self.articles_count = 0
        self.progress_bar = tqdm(desc="Scraping articles", unit="article", total=(4+28)*2*10)

        # Setup mongodb connection
        self.collection = get_mongodb_collection()

        # Disable scrapy and mongodb logging
        logging.getLogger('scrapy').setLevel(logging.WARNING)
        logging.getLogger('pymongo').setLevel(logging.WARNING)

    # Start crawling articles using the keywords on first page_count pages
    def start_requests(self):
        for page in range(4):
            url_value = self.base_url.format(page=page, category=1)
            yield scrapy.Request(url_value, self.parse)
        for page in range(28):
            url_value = self.base_url.format(page=page, category=2)
            yield scrapy.Request(url_value, self.parse)

    def parse(self, response):
        # Extract article links from the search page
        article_links = response.css('section.listing h2.atitle a::attr(href)').getall()

        # Follow each article link
        for link in article_links:
            yield response.follow(link, self.parse_article)

    def parse_article(self, response):
        TEXT_SELECTOR = 'p:not([class])::text'
        TITLE_SELECTOR = 'h1.title::text'
        
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
        'DOWNLOAD_DELAY': 5
    })
    process.crawl(VesselfinderSpider)
    process.start()