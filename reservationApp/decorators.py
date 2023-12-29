from django.http import HttpResponse
from django.shortcuts import redirect


def unauthenticatedUser(viewFunc):
    def wrappedFunc(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        else:
            return viewFunc(request, *args, **kwargs)
    return wrappedFunc


def allowedUsers(allowedGroups=[]):
    def decorator(viewFunc):
        def wrappedFunc(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                userGroups = []
                for userGroup in request.user.groups.all():
                    userGroups.append(userGroup.name)
            if any(group in userGroups for group in allowedGroups):
                return viewFunc(request, *args, **kwargs)
            else:
                return HttpResponse("Nie masz uprawnien zeby to widziec")
        return wrappedFunc
    return decorator
