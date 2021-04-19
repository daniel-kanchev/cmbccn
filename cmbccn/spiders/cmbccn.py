import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from cmbccn.items import Article


class cmbccnSpider(scrapy.Spider):
    name = 'cmbccn'
    start_urls = ['http://en.cmbc.com.cn/HomePage/Foot/footlocaltion/CMBCNews/CMBCNews/index.htm']

    def parse(self, response):
        articles = response.xpath('//ul[@class="ListUl"]/li')
        for article in articles:
            link = article.xpath('./a/@href').get()
            date = article.xpath('./span/text()').get()
            if date:
                date = " ".join(date.split())

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[text()="Next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2[@class="font16"]/a/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//dl[@class="detailBox"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
