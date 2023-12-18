from django.conf import settings
from .models import UserProfile


def userRole(request):
    currentUser = request.user
    isAdmin = currentUser.groups.filter(name='admin').exists()
    if isAdmin:
        return {'userRole': 'admin'}
    isController = currentUser.groups.filter(name='controller').exists()
    if isController:
        return {'userRole': 'controller'}
    isServiceProvider = currentUser.groups.filter(name='serviceProvider').exists()
    if isServiceProvider:
        return {'userRole': 'serviceProvider'}
    return {'userRole': 'client'}


def userPicture(request):
    defaultImage = settings.MEDIA_URL + 'default.jpg'
    if request.user.is_authenticated:
        userProfile = UserProfile.objects.filter(user=request.user).first()
        if userProfile and userProfile.profileImage:
            profileImageUrl = userProfile.profileImage.url
        else:
            profileImageUrl = defaultImage
    else:
        profileImageUrl = defaultImage
    return {'profileImageUrl': profileImageUrl}
