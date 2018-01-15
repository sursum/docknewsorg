from wagtail.wagtailcore.models import Orderable
from blog.models import BlogCategory
from django import template

register = template.Library()

@register.simple_tag
def get_categories():    
    return BlogCategory.objects.all()
    