from wagtail.wagtailcore.models import Orderable
from blog.models import BlogCategory, BlogPage
from blog.submodels.utility_models import *
from django import template

register = template.Library()

@register.simple_tag
def get_categories():    
    return BlogCategory.objects.all()
    
@register.simple_tag
def get_blogsbycat(cat_name):    
    return BlogPage.objects.filter(categories__name=cat_name).live().order_by('-first_published_at')    

@register.simple_tag
def get_piratequotes(tag_name):    
    return BlogPage.objects.filter(tag__name=tag_name).live().order_by('-first_published_at')    


@register.simple_tag
def random_quote():
    """
    Returns a random quote
    """
    quote = Quote.objects.order_by('?').values()[0]
    # quote = Quote.objects.order_by('?')[0]
    print(quote)
    return quote
