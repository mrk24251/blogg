from django import template
from blog.models import Post
from django.db.models import Count
from taggit.models import Tag

register = template.Library()

@register.simple_tag
def total_posts():
    return Post.published.count()

# @register.inclusion_tag('blog/post/latest_posts.html')
# def show_latest_posts(count=5):
#     latest_posts = Post.published.order_by('-publish')[:count]
#     return {'latest_posts': latest_posts}

@register.simple_tag
def show_latest_posts(count=3):
    latest_posts = Post.published.order_by('-publish')[:count]
    return latest_posts

@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(
        total_comments=Count('comments')
        )[:count]

@register.simple_tag
def get_All_Tags(count=10):
    tag_names = [tag for tag in Tag.objects.all()]
    tags=tag_names[:count]
    return tags

from django.utils.safestring import mark_safe
import markdown

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))