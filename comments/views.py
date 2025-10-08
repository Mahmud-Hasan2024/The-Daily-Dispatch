from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Comment
from .forms import CommentForm
from news.models import Article

# Create your views here.

@login_required
def comment_create(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    form = CommentForm()

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.article = article
            comment.save()

            return redirect("news:article_detail", slug=article.slug)
        
    return redirect("news:article_detail", slug=article.slug)


@login_required
def comment_update(request, pk):
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    form = CommentForm(instance=comment)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            form.save()

            return redirect("news:article_detail", slug=comment.article.slug)
        
    return render(request, "comments/comment_form.html", {"form": form, "comment": comment})


@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    article_slug = comment.article.slug

    if request.method == "POST":
        comment.delete()

        return redirect("news:article_detail", slug=article_slug)
    
    return render(request, "comments/comment_confirm_delete.html", {"comment": comment})
