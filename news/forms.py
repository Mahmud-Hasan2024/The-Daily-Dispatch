from django import forms
from news.models import Article, Category

class AdminArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "content", "image", "category", "status"]
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "textarea w-full h-32 resize-none"
            }),
        }

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "content", "image", "category"]
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "textarea w-full h-32 resize-none"
            }),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={
                "class": "textarea w-full h-24 resize-none"
            }),
        }
