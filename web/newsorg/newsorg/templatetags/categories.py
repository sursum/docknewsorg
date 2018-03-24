from wagtail.wagtailcore.models import Orderable
from blog.models import BlogCategory, BlogPage
from django import template

register = template.Library()

@register.simple_tag
def get_categories():    
    return BlogCategory.objects.all()
    
@register.simple_tag
def get_blogsbycat(cat_name):    
    return BlogPage.objects.filter(categories__name=cat_name).live().order_by('-first_published_at')    