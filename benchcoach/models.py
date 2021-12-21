from django.db import models
from django.core.validators import FileExtensionValidator


class Team(models.Model):
    name = models.CharField(max_length=50)
    image = models.FileField(
        upload_to="images/",
        validators=[FileExtensionValidator(["jpg", "png", "svg"])],
        null=True,
    )

    def __str__(self):
        return f"{self.name}"


class Venue(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"


class Event(models.Model):
    start = models.DateTimeField(null=True)
    venue = models.ForeignKey(Venue, null=True, on_delete=models.CASCADE)
    home_team = models.ForeignKey(
        Team, null=True, on_delete=models.CASCADE, related_name="home_team"
    )
    away_team = models.ForeignKey(
        Team, null=True, on_delete=models.CASCADE, related_name="away_team"
    )

    def __str__(self):
        return f"{self.start:%Y-%m-%d %H:%M}"


class Season(models.Model):
    name = models.CharField(max_length=50)


class Player(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    jersey_number = models.IntegerField(null=True)
    team = models.ForeignKey(Team, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    class Meta:
        unique_together = (
            "first_name",
            "last_name",
        )


class StatLine(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    batting_avg = models.DecimalField(max_digits=4, decimal_places=3, default=0)
    onbase_pct = models.DecimalField(max_digits=4, decimal_places=3, default=0)
    slugging_pct = models.DecimalField(max_digits=4, decimal_places=3, default=0)

    def __str__(self):
        return f"{self.slash_line}"

    @property
    def slash_line(self):
        return "/".join(
            [
                f"{self.batting_avg:.3f}".lstrip("0"),
                f"{self.onbase_pct:.3f}".lstrip("0"),
                f"{self.slugging_pct:.3f}".replace("0.", "."),
            ]
        )


class Positioning(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    positions = [
        ("EH", "EH"),
        ("P", "P"),
        ("C", "C"),
        ("1B", "1B"),
        ("2B", "2B"),
        ("3B", "3B"),
        ("SS", "SS"),
        ("LF", "LF"),
        ("CF", "CF"),
        ("RF", "RF"),
        ("DH", "DH"),
    ]
    position = models.CharField(
        choices=positions, default=None, max_length=2, null=True, blank=True
    )
    order = models.PositiveSmallIntegerField(default=None, null=True, blank=True)

    class Meta:
        unique_together = (
            "player",
            "event",
        )

    def __str__(self):
        return f"{self.player}; {self.event};"


class Availability(models.Model):
    YES = 2
    MAYBE = 1
    NO = 0
    UNKNOWN = -1

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    choices = [(YES, "Yes"), (NO, "No"), (MAYBE, "Maybe"), (UNKNOWN, "Unknown")]
    available = models.IntegerField(choices=choices, default=UNKNOWN)

    def __str__(self):
        return f"{self.event}; {self.player}; {self.available}"

    class Meta:
        unique_together = (
            "event",
            "player",
        )
        verbose_name_plural = "availabilities"
