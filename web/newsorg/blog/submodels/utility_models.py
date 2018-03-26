from __future__ import absolute_import, unicode_literals
from django import forms
from django.db import models
from django.utils import timezone

from wagtail.wagtailcore import blocks
from modelcluster.fields import ParentalKey

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import StreamField, RichTextField

from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel, PageChooserPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock

from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet

# from blog.models import BucStreamBlock
#########################################
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



#########################################
@register_snippet
class Quote(models.Model):
    title = models.CharField(max_length=30, help_text="Enter the title of the quote", blank=True)
    quote = RichTextField()
    by = models.CharField(max_length=30, help_text="Enter the quote year - book, author", blank=True)
    
    def __str__(self):
        return (self.quote)

    content_panels = [
        FieldPanel('title'),
        FieldPanel('quote'),
        FieldPanel('by'),        
    ]
    
# Create a Profile class
class PersonBlock(blocks.StructBlock):
    first_name = blocks.CharBlock()
    surname = blocks.CharBlock()        
    email = blocks.EmailBlock()
    photo = ImageChooserBlock(required=False)
    biography = blocks.RichTextBlock()

    class Meta:
        icon = 'user'

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


