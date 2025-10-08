from django.shortcuts import redirect

def logout_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("news:article_list")
        return view_func(request, *args, **kwargs)
    return wrapper
