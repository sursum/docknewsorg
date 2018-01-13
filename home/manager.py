# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy.orm import sessionmaker
from bucscraper.bucscraper.models import BucscraperDB, db_connect, create_table
from blog import BlogPage

class ScrapyManager(object):
    def __init__(self):
        """Initializes database connection and sessionmaker.
        Creates deals table.
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self):
        """Save deals in the database.
        session.query(BucscraperDB).filter_by(name='ed').all()
objects.live().order_by('-first_published_at')
        print(blogs)
        This method is called for every item pipeline component.
        """
        session = self.Session()
        try:
            scraper = session.query(BucscraperDB).all()
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        
        blogpage = BlogPage()
        blogpage.intro = item["text"]
        blogpage.url = item["link"]
