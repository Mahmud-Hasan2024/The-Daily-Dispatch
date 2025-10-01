from django import forms
from news.models import Article, Category

class AdminArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "content", "image", "category", "status"]

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "content", "image", "category"]

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]