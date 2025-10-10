from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from users.forms import EditUserForm, GroupForm, RegisterForm, User, AssignRoleForm, EditProfileForm, CustomPasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from users.utils import is_admin, is_editor, is_reporter
from news.models import Article, Category
from users.models import Profile
from django.contrib.auth.models import Group, User, Permission
from users.decorators import logout_required
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.views.generic import DetailView
from users.utils import get_user_role


# Create your views here.

# Authentication Views

@logout_required
def signup_view(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data.get('email')
            user.is_active = False
            user.save()
            messages.success(request, 'A confirmation mail sent. Please check your email')
            return redirect('users:login')
    return render(request, 'users/signup.html', {"form": form})


@logout_required
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("news:article_list")
    else:
        form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})

@login_required
def logout_view(request):
    logout(request)
    return redirect("news:article_list")


# Account Activation View
def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('users:login')
        else:
            return HttpResponse('Invalid Id or token')

    except User.DoesNotExist:
        return HttpResponse('User not found')
    


# ---------------- Admin Dashboard ----------------

@login_required
@user_passes_test(is_admin, login_url='users:no_permission')
def admin_dashboard(request):
    # Article stats
    total_articles = Article.objects.count()
    pending_articles = Article.objects.filter(status="pending")
    published_articles = Article.objects.filter(status="published")
    categories_count = Category.objects.count()
    users_count = User.objects.count()

    # Articles per category
    category_articles = {c.name: c.articles.count() for c in Category.objects.all()}

    # Role/Group management
    groups = Group.objects.prefetch_related("permissions").all()
    users = User.objects.all()

    context = {
        "total_articles": total_articles,
        "pending_articles_count": pending_articles.count(),
        "published_articles_count": published_articles.count(),
        "categories_count": categories_count,
        "users_count": users_count,
        "pending_articles": pending_articles,
        "published_articles": published_articles,
        "category_articles": category_articles,
        "groups": groups,
        "users": users,
        "permissions": Permission.objects.all(),
    }
    return render(request, "users/admin_dashboard.html", context)



# ---------------- Editor Dashboard ----------------
@login_required
@user_passes_test(is_editor, login_url='users:no_permission')
def editor_dashboard(request):
    total_articles = Article.objects.count()
    pending_articles = Article.objects.filter(status="pending")
    published_articles = Article.objects.filter(status="published")

    context = {
        "total_articles": total_articles,
        "pending_articles_count": pending_articles.count(),
        "published_articles_count": published_articles.count(),
        "pending_articles": pending_articles,
        "published_articles": published_articles,
    }
    return render(request, "users/editor_dashboard.html", context)


# ---------------- Reporter Dashboard ----------------
@login_required
@user_passes_test(is_reporter, login_url='users:no_permission')
def reporter_dashboard(request):
    my_articles = Article.objects.filter(author=request.user)
    my_pending = my_articles.filter(status="pending")
    my_published = my_articles.filter(status="published")

    context = {
        "my_articles": my_articles,
        "my_articles_count": my_articles.count(),
        "my_pending_count": my_pending.count(),
        "my_published_count": my_published.count(),
    }
    return render(request, "users/reporter_dashboard.html", context)


@login_required
@user_passes_test(is_admin, login_url='users:no_permission')
def assign_role(request, user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = get_object_or_404(User, pk=user_id)
    form = AssignRoleForm()

    if request.method == 'POST':
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            user.groups.clear()
            user.groups.add(role)
            messages.success(request, f"{user.username} assigned to {role.name} successfully.")
            return redirect('users:user_list')

    return render(request, 'users/assign_role.html', {"form": form, "user": user})


# user management views

@login_required
@user_passes_test(is_admin, login_url='users:no_permission')
def user_list(request):
    users = User.objects.all()
    return render(request, "users/user_list.html", {"users": users})


@login_required
@user_passes_test(is_admin, login_url='users:no_permission')
def edit_user_roles(request, pk):
    user = get_object_or_404(User, id=pk)
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



# group management views

@login_required
@user_passes_test(is_admin, login_url='users:no_permission')
def group_list(request):
    groups = Group.objects.all()
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
@user_passes_test(is_admin  , login_url='users:no_permission')
def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk)


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


# Profile Management Views

class ProfileView(DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_role'] = get_user_role(self.request)
        return context


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

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

    


# Change Password

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

# no permission view
def no_permission(request):
    return render(request, "users/no_permission.html")