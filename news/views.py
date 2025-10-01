from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from news.models import Article, Category
from news.forms import AdminArticleForm, ArticleForm, CategoryForm
from comments.forms import CommentForm
from django.core.paginator import Paginator
from users.utils import is_admin_editor_reporter, is_admin, is_editor, is_reporter, is_moderator
from django.contrib import messages
from django.urls import reverse

# Create your views here.

# Article Views
def article_list(request):
    featured = Article.objects.filter(status="published").order_by("-created_at").first()
    articles_list = Article.objects.filter(status="published").order_by("-created_at")[1:]

    paginator = Paginator(articles_list, 6)
    page_number = request.GET.get("page")
    articles = paginator.get_page(page_number)

    categories = Category.objects.all()
    trending = Article.objects.filter(status="published").order_by("-created_at")[:5]

    return render(request, "articles/article_list.html", {
        "featured": featured,
        "articles": articles,
        "categories": categories,
        "trending": trending,
    })


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, status="published")
    comment_form = CommentForm()
    related = Article.objects.filter(category=article.category, status="published").exclude(id=article.id)[:5]

    if request.method == "POST" and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.article = article
            comment.save()
            return redirect("news:article_detail", slug=slug)

    return render(request, "articles/article_detail.html", {
        "article": article,
        "comment_form": comment_form,
        "related": related,
    })




# CRUD for Articles (Admin, Editor, Reporter)

@login_required
@user_passes_test(is_admin_editor_reporter, login_url='users:no_permission')
def create_article(request):
    if is_admin(request.user) or is_editor(request.user):
        form_class = AdminArticleForm
    elif is_reporter(request.user):
        form_class = ArticleForm
    else:
        return redirect("users:no_permission")

    if request.method == "POST":
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            if is_reporter(request.user):
                article.status = "pending"
            article.save()
            return redirect("news:article_detail", slug=article.slug)
    else:
        form = form_class()

    return render(request, "articles/article_form.html", {"form": form})


@login_required
@user_passes_test(is_admin_editor_reporter, login_url='users:no_permission')
def update_article(request, slug):
    article = get_object_or_404(Article, slug=slug)

    # reporter can edit only their own articles
    if is_reporter(request.user) and article.author != request.user:
        return redirect("users:no_permission")

    # choose correct form
    if is_admin(request.user) or is_editor(request.user):
        form_class = AdminArticleForm
    else:
        form_class = ArticleForm

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=article)
        if form.is_valid():
            updated_article = form.save(commit=False)

            if is_reporter(request.user):
                # reporter’s edits always need re-approval
                updated_article.status = "pending"
            else:
                # admin/editor can freely change status
                pass  

            updated_article.save()
            return redirect("news:article_list")
    else:
        form = form_class(instance=article)

    return render(request, "articles/article_form.html", {"form": form, "article": article})



@login_required
@user_passes_test(is_admin or is_editor or is_reporter, login_url='users:no_permission')
def delete_article(request, slug):
    article = get_object_or_404(Article, slug=slug)

    if is_reporter(request.user) and article.author != request.user:
        return redirect("users:no_permission")

    if request.method == "POST":
        article.delete()
        return redirect("news:article_list")

    return render(request, "articles/article_confirm_delete.html", {"article": article})

@login_required
@user_passes_test(is_admin or is_editor, login_url='users:no_permission')
def review_articles(request):
    pending_articles = Article.objects.filter(status="pending")
    return render(request, "articles/review_articles.html", {"pending_articles": pending_articles})



@login_required
@user_passes_test(is_admin or is_editor, login_url='users:no_permission')
def approve_article(request, pk):
    article = get_object_or_404(Article, pk=pk, status="pending")
    article.status = "published"
    article.save()
    messages.success(request, f"Article '{article.title}' has been approved and published.")
    return redirect(reverse("users:admin_dashboard"))


@login_required
@user_passes_test(is_admin or is_editor, login_url='users:no_permission')
def reject_article(request, pk):
    article = get_object_or_404(Article, pk=pk, status="pending")
    article.delete()
    messages.warning(request, f"Article '{article.title}' has been rejected and deleted.")
    return redirect(reverse("users:admin_dashboard"))



# Category Views

def category_list(request):
    categories = Category.objects.all()
    return render(request, "categories/category_list.html", {"categories": categories})


def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    articles = Article.objects.filter(category=category, status="published").order_by("-created_at")
    return render(request, "categories/category_detail.html", {"category": category, "articles": articles})


@login_required
@user_passes_test(is_admin or is_editor, login_url='users:no_permission')
def create_category(request):
    form = CategoryForm()

    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("news:category_list")
        
    return render(request, "categories/category_form.html", {"form": form})


@login_required
@user_passes_test(is_admin or is_editor, login_url='users:no_permission')
def update_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(instance=category)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            return redirect("news:category_detail", pk=pk)
        
    return render(request, "categories/category_form.html", {"form": form, "category": category})


@login_required
@user_passes_test(is_admin or is_editor, login_url='users:no_permission')
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        category.delete()
        return redirect("news:category_list")
    
    return render(request, "categories/category_confirm_delete.html", {"category": category})