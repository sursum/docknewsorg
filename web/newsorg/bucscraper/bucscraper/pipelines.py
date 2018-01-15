# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from sqlalchemy.orm import sessionmaker
from slugify import slugify

from django.core.exceptions import ValidationError

from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.rich_text import RichText
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page

from bucscraper.models import BucscraperDB, db_connect, create_table
from blog.models import BlogPage

def truncate_string(content, numberofwords=12, suffix='...'):
    if len(content) <= numberofwords:
            return content
    else:
        return ' '.join(content.split()[:numberofwords]) + suffix

class BucscraperPipeline(object):
    def __init__(self):
        """Initializes database connection and sessionmaker.
        Creates deals table.
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """Save articles in the database.

        This method is called for every item pipeline component.
        """        
        text_index = Page.objects.filter(title="Minitrue Index").first()
            
        slug_path = slugify(truncate_string(item["text"],5, ''))
        blogtitle = truncate_string(item["text"],8)
        blogpage = BlogPage()
        blogpage.tags.add('minitrue')
        blogpage.body = [            
            ('paragraph', RichText(item["text"])),
            # ('image', ImageChooserBlock()),
            #('articleIP', blocks.URLBlock(item["link"])),
            ('articleIP', json.dumps(item["link"]).strip("\"")),
        ]
        try:
            text_index.add_child(instance=BlogPage(title=blogtitle, 
                                    slug=slug_path, 
                                    intro = truncate_string(item["text"],25),
                                    body = blogpage.body,  
                                    tags = blogpage.tags,      
            ))
        # try:
        #     text_index.add_child(instance=BlogPage(title=blogtitle, 
        #                             slug=slug_path, 
        #                             intro = truncate_string(item["text"],25),
        #                             body = blogpage.body))
        except ValidationError as err:
            print(str(err) )

        return item