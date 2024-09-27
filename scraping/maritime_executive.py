import scrapy
from scrapy.crawler import CrawlerProcess
from tqdm import tqdm
import logging

# Import from utils
from utils import Article, get_mongodb_collection, clean_text

class MaritimeExecutiveSpider(scrapy.Spider):
    name = 'maritime-executive'
    base_url = 'https://www.maritime-executive.com/search?key={keyword}&page={page}'
    
    def __init__(self, *args, **kwargs):
        super(MaritimeExecutiveSpider, self).__init__(*args, **kwargs)
        self.page_count = 10
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
        self.collection = get_mongodb_collection()

        # Disable scrapy and mongodb logging
        logging.getLogger('scrapy').setLevel(logging.WARNING)
        logging.getLogger('pymongo').setLevel(logging.WARNING)

    # Start crawling articles using the keywords on first page_count pages
    def start_requests(self):
        for key in self.keywords:
            for i in range(1, self.page_count + 1):
                yield scrapy.Request(self.base_url.format(keyword=key, page=i), self.parse)

    def parse(self, response):
        # Extract article links from the search page
        article_links = response.css('div.list-group button a::attr(href)').getall()
        
        # Follow each article link
        for link in article_links:
            yield response.follow(link, self.parse_article)

    def parse_article(self, response):
        if 'article' in response.url and 'editorial' not in response.url:
            TEXT_SELECTOR = 'p:not([class])::text'
            TITLE_SELECTOR = 'h1::text'

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
            self.collection.insert_one(article.to_dict())
            
            self.articles_count += 1
            self.progress_bar.update(1)

            yield article.to_dict()
        else:
            self.logger.info(f"Skipping non-article or editorial URL: {response.url}")
    def closed(self, reason):
        self.progress_bar.close()
        print(f"\nTotal articles scraped: {self.articles_count}")

if __name__ == '__main__':
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    })
    process.crawl(MaritimeExecutiveSpider)
    process.start()