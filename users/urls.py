from django.urls import path
from users.views import signup_view, login_view, logout_view, activate_user
from users.views import (
    admin_dashboard, editor_dashboard, reporter_dashboard,
    assign_role, create_group, group_list, no_permission
)

app_name = "users"

urlpatterns = [
    # ---------------- Auth ----------------
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("activate/<int:user_id>/<str:token>/", activate_user, name="activate"),

    # ---------------- Dashboards ----------------
    path("admin/", admin_dashboard, name="admin_dashboard"),
    path("editor/", editor_dashboard, name="editor_dashboard"),
    path("reporter/", reporter_dashboard, name="reporter_dashboard"),

    # ---------------- User & Group Management ----------------
    path("assign-role/<int:user_id>/", assign_role, name="assign_role"),
    path("create-group/", create_group, name="create_group"),
    path("group-list/", group_list, name="group_list"),
    path("no-permission/", no_permission, name="no_permission"),
]
