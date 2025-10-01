def is_admin_editor_reporter(user):
    return is_admin(user) or is_editor(user) or is_reporter(user)

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
    return user.is_not_authenticated