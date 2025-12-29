from django.db import models
from django.contrib.auth.models import User


class Deck(models.Model):
    MODE_CHOICES = [
        ("hybrid", "Hybrid"),
        ("fixed", "Fixed"),
    ]

    UNIT_CHOICES = [
        ("min", "Minutes"),
        ("hour", "Hours"),
        ("day", "Days"),
        ("week", "Weeks"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="decks")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")

    schedule_mode = models.CharField(max_length=10, choices=MODE_CHOICES, default="hybrid")

    # Store all as minutes (authoritative), plus unit preference for UI
    again_minutes = models.PositiveIntegerField(default=10)
    again_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="min")

    hard_minutes = models.PositiveIntegerField(default=60)
    hard_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="min")

    good_minutes = models.PositiveIntegerField(default=1440)  # 1 day
    good_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="day")

    easy_minutes = models.PositiveIntegerField(default=4320)  # 3 days
    easy_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="day")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user_id})"


class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cards")
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name="cards")

    front = models.TextField()
    back = models.TextField()
    tags = models.JSONField(default=list, blank=True)

    due_at = models.DateTimeField()
    interval_days = models.FloatField(default=0.0)
    ease = models.FloatField(default=2.3)
    reps = models.IntegerField(default=0)
    lapses = models.IntegerField(default=0)

    # latency / recall quality stats
    avg_think_ms = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Card({self.id}) deck={self.deck_id} user={self.user_id}"
