from django.db import models
from teamsnap.models import User as TeamsnapUser
from django.contrib.auth.models import User


def user_directory_path(instance, filename):
   # file will be uploaded to MEDIA_ROOT / user_<id>/<filename>
   return 'benchcoach/static/user_files/user_{0}/{1}'.format(instance.user.id, filename)

class Profile(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   teamsnap_access_token = models.CharField(null=True, max_length=50)
   teamsnap_user = models.ForeignKey(TeamsnapUser, on_delete=models.CASCADE, null=True)
   avatar = models.ImageField(upload_to="avatar", null=True, blank=True)