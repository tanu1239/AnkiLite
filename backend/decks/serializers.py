from rest_framework import serializers
from .models import Deck, Card

VALID_UNITS = {"min", "hour", "day", "week"}


class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = [
            "id",
            "name",
            "description",
            "schedule_mode",
            "again_minutes",
            "again_unit",
            "hard_minutes",
            "hard_unit",
            "good_minutes",
            "good_unit",
            "easy_minutes",
            "easy_unit",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        # Validate units
        for k in ["again_unit", "hard_unit", "good_unit", "easy_unit"]:
            if k in attrs and attrs[k] not in VALID_UNITS:
                raise serializers.ValidationError({k: "unit must be one of min|hour|day|week"})

        # Validate minutes are positive (or allow 0? we keep >=1 to avoid weird scheduling)
        for k in ["again_minutes", "hard_minutes", "good_minutes", "easy_minutes"]:
            if k in attrs:
                v = attrs[k]
                if v is None or int(v) < 1:
                    raise serializers.ValidationError({k: "must be an integer >= 1"})

        # schedule_mode
        if "schedule_mode" in attrs and attrs["schedule_mode"] not in {"fixed", "hybrid"}:
            raise serializers.ValidationError({"schedule_mode": "must be fixed or hybrid"})

        return attrs


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = [
            "id",
            "deck",
            "front",
            "back",
            "tags",
            "due_at",
            "interval_days",
            "ease",
            "reps",
            "lapses",
            "avg_think_ms",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "due_at",
            "interval_days",
            "ease",
            "reps",
            "lapses",
            "avg_think_ms",
            "created_at",
            "updated_at",
        ]
