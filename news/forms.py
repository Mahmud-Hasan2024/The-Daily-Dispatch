from django import forms
from news.models import Article, Category

class AdminArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "slug", "content", "image", "category", "status", "is_published"]

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "slug", "content", "image", "category"]

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]