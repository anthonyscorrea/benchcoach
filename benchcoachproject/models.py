from django.db import models
from teamsnap.models import User as TeamsnapUser, Team as TeamsnapTeam
from django.contrib.auth.models import User

class Profile(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   teamsnap_access_token = models.CharField(null=True, max_length=50)
   teamsnap_user = models.OneToOneField(
      TeamsnapUser,
      on_delete=models.CASCADE,
      null=True,
      blank=True,
      related_name="benchcoach_object"
   )
   avatar = models.ImageField(upload_to="avatar", null=True, blank=True)

class TeamsnapSettings(models.Model):
   user = models.OneToOneField(Profile, on_delete=models.CASCADE)
   managed_team = models.ForeignKey(TeamsnapTeam, on_delete=models.CASCADE)