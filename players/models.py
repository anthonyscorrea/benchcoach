from django.db import models
from teams.models import Team

class Player(models.Model):
   first_name = models.CharField(max_length=200)
   last_name = models.CharField(max_length=200)
   jersey_number = models.IntegerField()
   team = models.ForeignKey(Team, null=True, on_delete=models.CASCADE)

   def __str__(self):
      return f"{self.last_name}, {self.first_name}"

   class Meta:
      unique_together = ('first_name', 'last_name',)

class StatLine(models.Model):
   player = models.ForeignKey(Player, on_delete=models.CASCADE)
   batting_avg = models.DecimalField(max_digits=4, decimal_places=3, default=0)
   onbase_pct = models.DecimalField(max_digits=4, decimal_places=3, default=0)
   slugging_pct = models.DecimalField(max_digits=4, decimal_places=3, default=0)

   def __str__(self):
      return f"{self.slash_line}"

   @property
   def slash_line(self):
      return "/".join([
         f"{self.batting_avg:.3f}".lstrip("0"),
         f"{self.onbase_pct:.3f}".lstrip("0"),
         f"{self.slugging_pct:.3f}".replace("0.",".")
         ]
      )