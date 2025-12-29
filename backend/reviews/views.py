import logging
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from decks.models import Card, Deck
from decks.serializers import CardSerializer


from decks.models import Card
from decks.serializers import CardSerializer
from .scheduler import apply_review, priority_score
from .mongo import reviews_col

logger = logging.getLogger(__name__)


class DueCardsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        deck_id = request.query_params.get("deck_id")
        limit = int(request.query_params.get("limit", "50"))

        qs = Card.objects.filter(user=request.user, due_at__lte=now)
        if deck_id:
            qs = qs.filter(deck_id=deck_id)

        cards = list(qs[:500])  # safety cap before scoring
        scored = [(priority_score(c, now), c) for c in cards]
        scored.sort(key=lambda x: x[0], reverse=True)
        selected = [c for _, c in scored[:limit]]

        return Response(CardSerializer(selected, many=True).data)
    
class CramCardsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        deck_id = request.query_params.get("deck_id")
        limit = int(request.query_params.get("limit", "50"))

        qs = Card.objects.filter(user=request.user).order_by("due_at")
        if deck_id:
            # validate deck ownership
            ok = Deck.objects.filter(id=deck_id, user=request.user).exists()
            if not ok:
                return Response({"error": "deck not found"}, status=404)
            qs = qs.filter(deck_id=deck_id)

        cards = list(qs[:limit])
        return Response(CardSerializer(cards, many=True).data)


class ReviewCardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, card_id: int):
        grade_raw = request.data.get("grade")
        if grade_raw is None:
            return Response({"error": "grade required"}, status=400)

        try:
            grade = int(grade_raw)
        except ValueError:
            return Response({"error": "grade must be int 0..3"}, status=400)

        think_ms = request.data.get("think_ms")
        grade_ms = request.data.get("grade_ms")
        session_id = request.data.get("session_id")

        try:
            think_ms = int(think_ms) if think_ms is not None else None
            grade_ms = int(grade_ms) if grade_ms is not None else None
        except ValueError:
            return Response({"error": "think_ms / grade_ms must be integers"}, status=400)

        card = Card.objects.filter(id=card_id, user=request.user).first()
        if not card:
            return Response({"error": "card not found"}, status=404)

        now = timezone.now()
        apply_review(card, grade=grade, think_ms=think_ms, now=now)
        card.save()

        # Mongo event log (non-critical)
        try:
            reviews_col.insert_one({
                "user_id": request.user.id,
                "deck_id": card.deck_id,
                "card_id": card.id,
                "grade": grade,
                "think_ms": think_ms,
                "grade_ms": grade_ms,
                "total_ms": None if (think_ms is None or grade_ms is None) else (think_ms + grade_ms),
                "session_id": session_id,
                "reviewed_at": now,
            })
        except Exception as e:
            logger.warning("Mongo insert failed; skipping review log: %s", e)

        return Response({
            "ok": True,
            "card": CardSerializer(card).data
        })
