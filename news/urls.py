from django.urls import path
from news.views import (
    article_list, article_detail, create_article, update_article, delete_article,
    category_list, category_detail, create_category, update_category,delete_category,
    review_articles, approve_article, reject_article
)


app_name = "news"

urlpatterns = [
    path("", article_list, name="article_list"),

    # Article URLs
    path("article/create/", create_article, name="create_article"),
    path("article/<slug:slug>/", article_detail, name="article_detail"),
    path("article/<slug:slug>/update/", update_article, name="update_article"),
    path("article/<slug:slug>/delete/", delete_article, name="delete_article"),

    # Category URLs
    path("categories/", category_list, name="category_list"),
    path("categories/<int:pk>/", category_detail, name="category_detail"),
    path("categories/create/", create_category, name="create_category"),
    path("categories/<int:pk>/update/", update_category, name="update_category"),
    path("categories/<int:pk>/delete/", delete_category, name="delete_category"),

    # Review and Approve Articles
    path("articles/review/", review_articles, name="review-articles"),
    # path("articles/<int:pk>/approve/", approve_article, name="approve-article")
    path("approve-article/<int:pk>/", approve_article, name="approve_article"),
    path("reject-article/<int:pk>/", reject_article, name="reject_article"),
]
