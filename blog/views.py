from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage,\
PageNotAnInteger
from .form import EmailPostForm, EmailPostForm2, CommentForm,SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector,SearchQuery,SearchRank
from django.contrib.postgres.search import TrigramSimilarity
from jalali_date import datetime2jalali, date2jalali

from django.views.generic import ListView

# class PostListView(ListView):
#     queryset = Post.objects.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'

def post_list(request, tag_slug=None):
    object_list = Post.objects.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 4)  # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
    # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'page': page,
                   'posts': posts,
                   'tag': tag})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day,
        slug=post)

    # List of active comments for this post
    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            parent_obj=None
            try:
                parent_id=int(request.POST.get("parent_id"))
            except:
                parent_id=None

            if parent_id:
                parent_qs=Comment.objects.filter(id=parent_id)
                if parent_qs.exists() and parent_qs.count() == 1:
                    parent_obj=parent_qs[0]

            # parent_qs=Comment.objects.filter(id=2)[0]
            new_comment.parent= parent_obj

            reply_to_obj=None
            try:
                reply_to_id=int(request.POST.get("reply_to_id"))
            except:
                reply_to_id=None

            if reply_to_id:
                reply_to_qs=Comment.objects.filter(id=reply_to_id)
                if reply_to_qs.exists():
                    reply_to_obj=reply_to_qs[0]

            new_comment.reply_to = reply_to_obj

            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids) \
        .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
                        .order_by('-same_tags', '-publish')[:4]

    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form,
                   'similar_posts': similar_posts,
                   },
                    using=None)

def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm2(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = 'پیشنهاد عرفانی {}'.format(cd['name'])
            message = ' \nسلام دوست من ' \
                      ' \n{} با ایمیل {} پیشنهاد می کند پست {} را به آدرس {} مطالعه کنید \n' \
                      '\n{}\n'.format(cd['name'],cd['email'],post.title, post_url, cd['comments'])
            send_mail(subject, message, 'admin@myblog.com',
                      [cd['to']])
            sent = True
    else:
        form = EmailPostForm2()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent},
                                                    using=None)

def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.objects.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.3).order_by('-similarity')

    paginator = Paginator(results, 4)  # 3 posts in each page
    page = request.GET.get('page',1)
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer deliver the first page
        results = paginator.page(1)
    except EmptyPage:
    # If page is out of range deliver last page of results
        results = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/search.html',
                  {'page': page,
                    'form': form,
                    'query': query,
                    'results': results,
                   })