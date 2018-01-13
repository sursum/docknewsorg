from __future__ import absolute_import, unicode_literals
from django.db import models
from django import forms

from modelcluster.fields import ParentalKey
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailadmin.edit_handlers import PageChooserPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from wagtail.wagtailcore.blocks import TextBlock, StructBlock, CharBlock, FieldBlock, RichTextBlock, RawHTMLBlock, StreamBlock
# TextBlock, StructBlock, StreamBlock, FieldBlock, CharBlock, RichTextBlock, RawHTMLBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock

from blog.models import BlogPage

# Global Streamfield definition

class PullQuoteBlock(StructBlock):
    quote = TextBlock("quote title")
    attribution = CharBlock()

    class Meta:
        icon = "openquote"


class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'), ('right', 'Wrap right'), ('mid', 'Mid width'), ('full', 'Full width'),
    ))


class HTMLAlignmentChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('normal', 'Normal'), ('full', 'Full width'),
    ))


class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock()
    alignment = ImageFormatChoiceBlock()


class AlignedHTMLBlock(StructBlock):
    html = RawHTMLBlock()
    alignment = HTMLAlignmentChoiceBlock()

    class Meta:
        icon = "code"


class BucStreamBlock(StreamBlock):
    h2 = CharBlock(icon="title", classname="title")
    h3 = CharBlock(icon="title", classname="title")
    h4 = CharBlock(icon="title", classname="title")
    intro = RichTextBlock(icon="pilcrow")
    paragraph = RichTextBlock(icon="pilcrow")
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
        FieldPanel('title', classname="full title"),
        StreamFieldPanel('body'),
        InlinePanel('carousel_items', label="Carousel items"),
        InlinePanel('related_links', label="Related links"),

    ]

    def get_context(self, request):
        # Get the published blogs        
        blogs = BlogPage.objects.live().order_by('-first_published_at')
        print(blogs)
        # filter by tags
        main_feature_article = blogs.filter(tags__name='main') #Make sure only one! query_set mainfeature article        
        minitrue = blogs.filter(tags__name='minitrue') #query_set minitrue
        published_media = blogs.filter(tags__name='feature') #query_set published_media
        opinion = blogs.filter(categories__name='Opinion') #query_set opinion-carousell
        cat_pol = blogs.filter(categories__name='Politik') #query_set cat_pol
        cat_econ = blogs.filter(categories__name='Ekonomi') #query_set cat_econ
        cat_cult = blogs.filter(categories__name='Kultur') #query_set cat_cult
        cat_sci = blogs.filter(categories__name='Vetenskap') #query_set cat_sci
        cat_health = blogs.filter(categories__name='Hälsa') #query_set cat_health
        dockyard = blogs.filter(tags__name='Dockyard') #query_set dockyard
        #print(main_feature_article)

        # Update template context
        context = super(HomePage, self).get_context(request)
        context['main_feature_article'] = main_feature_article
        context['minitrue'] = minitrue
        context['published_media'] = published_media
        context['opinion'] = opinion
        context['cat_pol'] = cat_pol
        context['cat_econ'] = cat_econ
        context['cat_cult'] = cat_cult
        context['cat_sci'] = cat_sci
        context['cat_health'] = cat_health
        context['dockyard'] = dockyard

        return context

    
