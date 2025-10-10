# users/views.py
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.views.generic import DetailView
from django.db.models import Count
from users.forms import EditUserForm, GroupForm, EditProfileForm, CustomPasswordChangeForm
from users.models import Profile
from users.utils import get_user_role, is_admin, is_editor, is_reporter

from news.models import Article, Category


# ---------------- Authentication Views ----------------

@login_required
def logout_view(request):
    logout(request)
    return redirect("news:article_list")


def activate_user(request, user_id, token):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('users:login')
        return HttpResponse('Invalid Id or token')
    except User.DoesNotExist:
        return HttpResponse('User not found')


# ---------------- Dashboards ----------------

@login_required
@user_passes_test(is_admin, login_url='users:no_permission')
def admin_dashboard(request):
    total_articles = Article.objects.count()
    pending_articles_count = Article.objects.filter(status="pending").count()
    published_articles_count = Article.objects.filter(status="published").count()
    categories_count = Category.objects.count()
    users_count = Profile.objects.count()

    category_articles = Category.objects.annotate(article_count=Count("articles"))

    groups = Group.objects.prefetch_related("permissions").all()
    users = Profile.objects.select_related("user").all()

    context = {
        "total_articles": total_articles,
        "pending_articles_count": pending_articles_count,
        "published_articles_count": published_articles_count,
        "categories_count": categories_count,
        "users_count": users_count,
        "category_articles": category_articles,
        "groups": groups,
        "users": users,
        "permissions": Permission.objects.all(),
    }
    return render(request, "users/admin_dashboard.html", context)


@login_required
@user_passes_test(is_editor, login_url='users:no_permission')
def editor_dashboard(request):
    total_articles = Article.objects.count()
    pending_articles_count = Article.objects.filter(status="pending").count()
    published_articles_count = Article.objects.filter(status="published").count()

    context = {
        "total_articles": total_articles,
        "pending_articles_count": pending_articles_count,
        "published_articles_count": published_articles_count,
    }
    return render(request, "users/editor_dashboard.html", context)


@login_required
@user_passes_test(is_reporter, login_url='users:no_permission')
def reporter_dashboard(request):
    my_articles = Article.objects.filter(author=request.user)
    my_pending_count = my_articles.filter(status="pending").count()
    my_published_count = my_articles.filter(status="published").count()

    context = {
        "my_articles": my_articles,
        "my_articles_count": my_articles.count(),
        "my_pending_count": my_pending_count,
        "my_published_count": my_published_count,
    }
    return render(request, "users/reporter_dashboard.html", context)


# ---------------- User & Group Management ----------------

@login_required
@user_passes_test(is_admin, login_url='users:no_permission')
def user_list(request):
    users = Profile.objects.select_related("user").prefetch_related("user__groups").all()
    return render(request, "users/user_list.html", {"users": users})


@login_required
@user_passes_test(is_admin, login_url='users:no_permission')
def edit_user_roles(request, pk):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = get_object_or_404(User.objects.prefetch_related("groups"), id=pk)
    groups = Group.objects.all()

    if request.method == "POST":
        selected_group_id = request.POST.get("group")
        if selected_group_id:
            try:
                selected_group = Group.objects.get(id=int(selected_group_id))
                user.groups.clear()
                user.groups.add(selected_group)
                messages.success(request, f"{user.username}'s role updated to {selected_group.name}.")
            except Group.DoesNotExist:
                messages.error(request, "Selected role does not exist.")
        else:
            messages.error(request, "No role selected.")
        return redirect("users:user_list")

    return render(request, "users/user_roles_form.html", {"user": user, "groups": groups})


@login_required
@user_passes_test(is_admin, login_url='users:no_permission')
def group_list(request):
    groups = Group.objects.prefetch_related("permissions").all()
    return render(request, "users/group_list.html", {"groups": groups})


@login_required
@user_passes_test(is_admin, login_url='users:no_permission')
def group_create(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:admin_dashboard")
    else:
        form = GroupForm()
    return render(request, "users/group_form.html", {"form": form, "title": "Create Group"})


@login_required
@user_passes_test(is_admin, login_url='users:no_permission')
def group_edit(request, pk):
    group = get_object_or_404(Group.objects.prefetch_related("permissions"), pk=pk)
    if request.method == "POST":
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect("users:admin_dashboard")
    else:
        form = GroupForm(instance=group)
    return render(request, "users/group_form.html", {"form": form, "title": "Edit Group"})


@login_required
@user_passes_test(is_admin, login_url='users:no_permission')
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == "POST":
        group.delete()
        messages.warning(request, f"Group '{group.name}' has been deleted.")
        return redirect("users:group_list")
    return render(request, "users/group_confirm_delete.html", {"group": group})


# ---------------- Profile Management ----------------

class ProfileView(DetailView):
    model = Profile
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        profile, created = Profile.objects.select_related("user").get_or_create(user=self.request.user)
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_role'] = get_user_role(self.request)
        return context


@login_required
def edit_profile(request):
    profile, created = Profile.objects.select_related("user").get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=request.user)
        profile_form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('users:profile')
    else:
        user_form = EditUserForm(instance=request.user)
        profile_form = EditProfileForm(instance=profile)

    return render(request, 'users/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


# ---------------- Password Change ----------------

class ChangePassword(PasswordChangeView):
    template_name = 'users/change_password.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('users:change_password_done')

    def form_valid(self, form):
        messages.success(self.request, 'Your password was changed successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_role'] = get_user_role(self.request)
        return context


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'users/change_password_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_role'] = get_user_role(self.request)
        return context


# ---------------- No Permission ----------------

def no_permission(request):
    return render(request, "users/no_permission.html")
