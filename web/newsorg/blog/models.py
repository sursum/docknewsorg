from __future__ import absolute_import, unicode_literals
from django import forms
from django.db import models
from django.utils import timezone

from wagtail.wagtailcore import blocks
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase, Tag as TaggitTag

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel, PageChooserPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock

from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet

from blog.submodels.utility_models import *

# Snippets
@register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy = True

@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('icon'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'

class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super(BlogIndexPage, self).get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at')
        context['blogpages'] = blogpages
        return context

class BlogCategoryIndexPage(Page):
    intro = models.CharField(max_length=300, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    def get_categories(self):
        return BlogCategory.objects.all()
    

    def get_context(self, request):        
        # Filter by tag
        category = request.GET.get('category')        
        categories = BlogCategory.objects.all()
        

        # Update context to include only published posts, ordered by reverse-chron
        if category in (x.name for x in categories):            
            blogpages = BlogPage.objects.filter(categories__name=category).live().order_by('-first_published_at')
            context = super(BlogCategoryIndexPage, self).get_context(request)        
            context['blogpages'] = blogpages
        else:
            context = super(BlogCategoryIndexPage, self).get_context(request)        
            context['category_names'] = categories
        #print(context)
        return context

class BlogTagIndexPage(Page):
    intro = models.CharField(max_length=300, blank=True)

    def get_context(self, request):        
        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)  

        # Update template context
        context = super(BlogTagIndexPage, self).get_context(request)
        context['blogpages'] = blogpages
        return context

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('BlogPage', related_name='tagged_items')

class BlogPage(Page):
    date = models.DateField("Post date", default=timezone.now)
    intro = models.CharField(max_length=250, blank=True)
    main_feature = models.BooleanField(default=False)
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),        
        ('image', ImageChooserBlock()),
        ('articleIP', blocks.URLBlock()),
    ])    
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    categories = ParentalManyToManyField('blog.BlogCategory', blank=True)
    authors = models.CharField(max_length=255, default="Buckanjären")
            
    def main_image(self):
        gallery_item = self.gallery_images.first()        
        if gallery_item:
            return gallery_item.image
        else:
            print("--- no image")
            return None

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]
    

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
            FieldPanel('main_feature', widget=forms.CheckboxSelectMultiple),
        ], heading="Blog information"),
        FieldPanel('intro'),
        FieldPanel('authors'),
        StreamFieldPanel('body'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]

class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]


#####################################################################
#####################################################################
# Home Page

class HomePageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('HomePage', related_name='carousel_items')


class HomePageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('HomePage', related_name='related_links')

class HomePage(Page):
    body = StreamField(BucStreamBlock())
    #search_fields = Page.search_fields + [
     #   index.SearchField('body'),
    #]

    api_fields = ['body', 'carousel_items', 'related_links']
        
    class Meta:
        verbose_name = "Homepage"
    
    content_panels = Page.content_panels + [
        #FieldPanel('title', classname="full title"),
        StreamFieldPanel('body'),
        InlinePanel('carousel_items', label="Carousel items"),
        InlinePanel('related_links', label="Related links"),

    ]    

    def get_context(self, request):
        # Get the published blogs        
        blogs = BlogPage.objects.live().order_by('-first_published_at')
        #print(blogs)
        # get categories
        categories = BlogCategoryIndexPage.get_categories(self)
        
        
        # filter by tags        
        context = super(HomePage, self).get_context(request)
        context['main_feature_article'] = blogs.filter(tags__name='main') #Make sure only one! query_set mainfeature article
        context['minitrue'] =  blogs.filter(tags__name='minitrue') #query_set minitrue
        context['published_media'] =  blogs.filter(tags__name='feature') #query_set published_media
        
        # filter by categories
        for cat in categories:
            context[cat] = blogs.filter(categories__name=cat)
            #print(main_feature_article)
                
        return context

    
