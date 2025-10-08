from django.urls import path
from users.views import (
    signup_view, login_view, logout_view, activate_user,
    admin_dashboard, editor_dashboard, reporter_dashboard,
    assign_role, group_create, group_list, group_edit, group_delete,
    user_list, edit_user_roles, ProfileView, edit_profile,
    ChangePassword, CustomPasswordChangeDoneView, no_permission
)
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

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
    path("assign_role/<int:user_id>/", assign_role, name="assign_role"),
    path("no_permission/", no_permission, name="no_permission"),

    path("groups/", group_list, name="group_list"),
    path("groups/create/", group_create, name="group_create"),
    path("groups/<int:pk>/edit/", group_edit, name="group_edit"),
    path("groups/<int:pk>/delete/", group_delete, name="group_delete"),

    path("users/", user_list, name="user_list"),
    path("users/<int:pk>/edit-roles/", edit_user_roles, name="edit_user_roles"),


    # ---------------- Profile Management ----------------
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),

    # ---------------- Password Change ----------------
    path('change-password/', ChangePassword.as_view(), name='change_password'),
    path('change-password/done/', CustomPasswordChangeDoneView.as_view(), name='change_password_done'),

    # ---------------- Password Reset ----------------
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset_form.html",
            email_template_name="users/password_reset_email.html",
            success_url=reverse_lazy("users:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url=reverse_lazy("users:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

]
