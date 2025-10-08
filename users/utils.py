from django.contrib.auth import get_user_model

User = get_user_model()

def user_has_role(user, role_name):
    return user.groups.filter(name=role_name).exists()

def is_admin_editor_reporter(user):
    return is_admin(user) or is_editor(user) or is_reporter(user)

def is_admin_or_editor(user):
    return is_admin(user) or is_editor(user)

def is_admin(user):
    return user.is_authenticated and user.groups.filter(name="Admin").exists()

def is_editor(user):
    return user.is_authenticated and user.groups.filter(name="Editor").exists()

def is_reporter(user):
    return user.is_authenticated and user.groups.filter(name="Reporter").exists()

def is_moderator(user):
    return user.is_authenticated and user.groups.filter(name="Moderator").exists()

def is_subscriber(user):
    return user.is_authenticated and user.groups.filter(name="Subscriber").exists()

def is_guest(user):
    return not user.is_authenticated



def get_user_role(request):
    user = request.user
    if not user.is_authenticated:
        return None

    if is_admin(user):
        return "Admin"
    elif is_editor(user):
        return "Editor"
    elif is_reporter(user):
        return "Reporter"
    elif is_moderator(user):
        return "Moderator"
    elif is_subscriber(user):
        return "Subscriber"
    else:
        return "User"
