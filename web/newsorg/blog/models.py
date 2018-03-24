from __future__ import absolute_import, unicode_literals
from django import forms
from django.db import models
from django.utils import timezone

from wagtail.wagtailcore import blocks
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel, PageChooserPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock

from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet


# Create a Profile class
class PersonBlock(blocks.StructBlock):
    first_name = blocks.CharBlock()
    surname = blocks.CharBlock()        
    email = blocks.EmailBlock()
    photo = ImageChooserBlock(required=False)
    biography = blocks.RichTextBlock()

    class Meta:
        icon = 'user'

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
    intro = RichTextField(blank=True)

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
    
    def get_context(self, request):

        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)

        # Update template context
        context = super(BlogTagIndexPage, self).get_context(request)
        context['blogpages'] = blogpages
        return context

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
#####################################################################
#####################################################################
#####################################################################
#####################################################################



# Global Streamfield definition

class PullQuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock("quote title")
    attribution = blocks.CharBlock()

    class Meta:
        icon = "openquote"


class ImageFormatChoiceBlock(blocks.FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'), ('right', 'Wrap right'), ('mid', 'Mid width'), ('full', 'Full width'),
    ))


class HTMLAlignmentChoiceBlock(blocks.FieldBlock):
    field = forms.ChoiceField(choices=(
        ('normal', 'Normal'), ('full', 'Full width'),
    ))


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    caption = blocks.RichTextBlock()
    alignment = ImageFormatChoiceBlock()


class AlignedHTMLBlock(blocks.StructBlock):
    html = blocks.RawHTMLBlock()
    alignment = HTMLAlignmentChoiceBlock()

    class Meta:
        icon = "code"


class BucStreamBlock(blocks.StreamBlock):
    h2 = blocks.CharBlock(icon="title", classname="title")
    h3 = blocks.CharBlock(icon="title", classname="title")
    h4 = blocks.CharBlock(icon="title", classname="title")
    intro = blocks.RichTextBlock(icon="pilcrow")
    paragraph = blocks.RichTextBlock(icon="pilcrow")
    aligned_image = ImageBlock(label="Aligned image", icon="image")
    pullquote = PullQuoteBlock()
    aligned_html = AlignedHTMLBlock(icon="code", label='Raw HTML')
    document = DocumentChooserBlock(icon="doc-full-inverse")

# Abstract helper classes

class LinkFields(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
    ]

    api_fields = ['link_external', 'link_page', 'link_document']

    class Meta:
        abstract = True

class CarouselItem(LinkFields):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    embed_url = models.URLField("Embed URL", blank=True)
    caption = models.CharField(max_length=255, blank=True)
    
    panels = [
        ImageChooserPanel('image'),
        FieldPanel('embed_url'),
        FieldPanel('caption'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    api_fields = ['image', 'embed_url', 'caption'] + LinkFields.api_fields

    class Meta:
        abstract = True

class RelatedLink(LinkFields):
    title = models.CharField(max_length=255, help_text="Link title")

    panels = [
        FieldPanel('title'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    page = ParentalKey('HomePage', related_name='carousel_items')


    class Meta:
        abstract = True


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

    # def get_context(self, request):
    #     # Get the published blogs        
    #     blogs = BlogPage.objects.live().order_by('-first_published_at')
    #     print(blogs)
    #     # filter by tags
    #     main_feature_article = blogs.filter(tags__name='main') #Make sure only one! query_set mainfeature article        
    #     minitrue = blogs.filter(tags__name='minitrue') #query_set minitrue
    #     published_media = blogs.filter(tags__name='feature') #query_set published_media
    #     opinion = blogs.filter(categories__name='Opinion') #query_set opinion-carousell
    #     cat_pol = blogs.filter(categories__name='Politik') #query_set cat_pol
    #     cat_econ = blogs.filter(categories__name='Ekonomi') #query_set cat_econ
    #     cat_cult = blogs.filter(categories__name='Kultur') #query_set cat_cult
    #     cat_sci = blogs.filter(categories__name='Vetenskap') #query_set cat_sci
    #     cat_health = blogs.filter(categories__name='Hälsa') #query_set cat_health
    #     dockyard = blogs.filter(tags__name='Dockyard') #query_set dockyard
    #     #print(main_feature_article)

    #     # Update template context
    #     context = super(HomePage, self).get_context(request)
    #     context['main_feature_article'] = main_feature_article
    #     context['minitrue'] = minitrue
    #     context['published_media'] = published_media
    #     context['opinion'] = opinion
    #     context['cat_pol'] = cat_pol
    #     context['cat_econ'] = cat_econ
    #     context['cat_cult'] = cat_cult
    #     context['cat_sci'] = cat_sci
    #     context['cat_health'] = cat_health
    #     context['dockyard'] = dockyard

    #     return context

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

    
