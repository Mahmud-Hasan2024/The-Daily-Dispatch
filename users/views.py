from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from users.forms import RegisterForm, User
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from users.utils import is_admin, is_editor, is_reporter
from news.models import Article, Category
from users.forms import AssignRoleForm, CreateGroupForm
from django.contrib.auth.models import Group

# Create your views here.

def signup_view(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            user.is_active = False
            user.save()
            messages.success(request, 'A Confirmation mail sent. Please check your email')
            return redirect('users:login')

        else:
            print("Form is not valid")
    return render(request, 'users/signup.html', {"form": form})

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
    total_articles = Article.objects.count()
    pending_articles = Article.objects.filter(status="pending")
    published_articles = Article.objects.filter(status="published")
    categories_count = Category.objects.count()
    users_count = User.objects.count()

    # Articles per category
    category_articles = {}
    for cat in Category.objects.all():
        category_articles[cat.name] = Article.objects.filter(category=cat).count()

    context = {
        "total_articles": total_articles,
        "pending_articles_count": pending_articles.count(),
        "published_articles_count": published_articles.count(),
        "categories_count": categories_count,
        "users_count": users_count,
        "category_articles": category_articles,
        "pending_articles": pending_articles,
        "published_articles": published_articles,
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
@user_passes_test(is_reporter, login_url='no_permission')
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


@login_required
@user_passes_test(is_admin, login_url='users:no_permission')
def create_group(request):
    form = CreateGroupForm()

    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group '{group.name}' created successfully.")
            return redirect('users:group_list')

    return render(request, 'users/create_group.html', {'form': form})


@login_required
@user_passes_test(is_admin, login_url='users:no_permission')
def group_list(request):
    groups = Group.objects.prefetch_related('permissions').all()
    return render(request, 'users/group_list.html', {'groups': groups})


def no_permission(request):
    return render(request, 'users/no_permission.html')
