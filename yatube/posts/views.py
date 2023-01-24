from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm, CommentForm
from .models import Post, Group, User, Comment, Follow
from django.conf import settings
from django.views.decorators.cache import cache_page


def get_paginated_page(request, posts):
    paginator = Paginator(posts, settings.PAGINATOR_PAGES)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20, key_prefix='index_page')
def index(request):
    """Главная страница."""
    template = 'posts/index.html'
    posts = Post.objects.all()
    page_obj = get_paginated_page(request, posts)
    context = {
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Cтраница последних записей группы."""
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-created')
    page_obj = get_paginated_page(request, posts)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Профиль пользователя."""
    author = get_object_or_404(User, username=username)
    posts = author.posts.all().order_by('-created')
    posts_count = author.posts.count
    following = author.following.exists()
    context = {
        'author': author,
        'posts': posts,
        'page_obj': get_paginated_page(request, posts),
        'posts_count': posts_count,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Подробная информация о посте."""
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('-created')
    form = CommentForm()
    post_count = post.author.posts.count()
    context = {
        'post': post,
        'post_count': post_count,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Cоздание поста."""
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Редактирование поста."""
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post,
                    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    follower = Follow.objects.filter(user=request.user).values_list(
        'author_id', flat=True
    )
    posts = Post.objects.filter(author_id__in=follower)
    context = {
        'page_obj': get_paginated_page(request, posts),
        'title': 'Подписки'
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow_obj = Follow.objects.filter(user=request.user, author=author)
    if request.user != author and not follow_obj.exists():
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:follow_index')
