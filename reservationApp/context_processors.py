from django.conf import settings
from .models import UserProfile


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
