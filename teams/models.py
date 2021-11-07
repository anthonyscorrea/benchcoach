from django.db import models
from django.core.validators import FileExtensionValidator

class Team(models.Model):
   name = models.CharField(max_length = 50)
   image = models.FileField(upload_to='images/', validators=[FileExtensionValidator(['jpg', 'png', 'svg'])], null=True)

   def __str__(self):
      return f"{self.name}"