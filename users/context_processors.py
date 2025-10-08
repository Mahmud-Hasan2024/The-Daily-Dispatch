from users.utils import is_admin, is_editor, is_reporter

def user_roles(request):
    if request.user.is_authenticated:
        return {
            "is_admin_user": is_admin(request.user),
            "is_editor_user": is_editor(request.user),
            "is_reporter_user": is_reporter(request.user),
        }
    return {
        "is_admin_user": False,
        "is_editor_user": False,
        "is_reporter_user": False,
    }
