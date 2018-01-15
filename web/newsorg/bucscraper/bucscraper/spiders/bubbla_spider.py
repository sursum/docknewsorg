import scrapy
from bucscraper.items import BucscraperItem

class BubblaSpider(scrapy.Spider):
    name = "bubbla"
    
    start_urls = [
        'https://bubb.la',
    ]

    def parse(self, response):
        pathtst ='//div[@class="view-content"]'
        # for quote in response.css('div.view-content'):
        #     yield {
        #         'text': quote.css('a.nodes::text').extract_first(),                
        #     }
        
        for sel in response.xpath(pathtst):
            
            item = BucscraperItem()
            item['text'] =  sel.xpath('.//*/a[@class="nodes"]/text()').extract_first()
            item['link'] =  sel.xpath('.//*/a[@class="nodes"]/@href').extract_first()
            
            yield item
            # yield {
            #     'text': sel.xpath('.//*/a[@class="nodes"]/text()').extract(),
            #     'link': sel.xpath('.//*/a[@class="nodes"]/@href').extract(),
            # }
        