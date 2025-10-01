from django.urls import path
from . import views

app_name = "comments"

urlpatterns = [
    path("create/<int:article_id>/", views.comment_create, name="comment_create"),
    path("update/<int:pk>/", views.comment_update, name="comment_update"),
    path("delete/<int:pk>/", views.comment_delete, name="comment_delete"),
]
