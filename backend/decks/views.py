from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from .models import Deck, Card
from .serializers import DeckSerializer, CardSerializer


class DecksView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Deck.objects.filter(user=request.user).order_by("-id")
        return Response(DeckSerializer(qs, many=True).data)

    def post(self, request):
        ser = DeckSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        deck = ser.save(user=request.user)
        return Response(DeckSerializer(deck).data, status=201)


class DeckDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, deck_id: int):
        deck = Deck.objects.filter(id=deck_id, user=request.user).first()
        if not deck:
            return Response({"error": "deck not found"}, status=404)

        ser = DeckSerializer(deck, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        deck = ser.save()
        return Response(DeckSerializer(deck).data)

    def delete(self, request, deck_id: int):
        deck = Deck.objects.filter(id=deck_id, user=request.user).first()
        if not deck:
            return Response({"error": "deck not found"}, status=404)
        deck.delete()
        return Response({"ok": True})


class DeckCardsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, deck_id: int):
        deck = Deck.objects.filter(id=deck_id, user=request.user).first()
        if not deck:
            return Response({"error": "deck not found"}, status=404)

        qs = Card.objects.filter(user=request.user, deck_id=deck_id).order_by("-id")
        return Response(CardSerializer(qs, many=True).data)

    def post(self, request, deck_id: int):
        deck = Deck.objects.filter(id=deck_id, user=request.user).first()
        if not deck:
            return Response({"error": "deck not found"}, status=404)

        front = request.data.get("front", "").strip()
        back = request.data.get("back", "").strip()
        tags = request.data.get("tags", [])

        if not front or not back:
            return Response({"error": "front and back required"}, status=400)

        now = timezone.now()
        card = Card.objects.create(
            user=request.user,
            deck=deck,
            front=front,
            back=back,
            tags=tags if isinstance(tags, list) else [],
            due_at=now,
            interval_days=0.0,
            ease=2.3,
            reps=0,
            lapses=0,
        )
        return Response(CardSerializer(card).data, status=201)


class ForceDueView(APIView):
    """
    Makes every card in a deck due now.
    Optional reset_progress=true resets reps/interval/ease/lapses.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, deck_id: int):
        deck = Deck.objects.filter(id=deck_id, user=request.user).first()
        if not deck:
            return Response({"error": "deck not found"}, status=404)

        reset = str(request.query_params.get("reset_progress", "false")).lower() in {"1", "true", "yes"}

        now = timezone.now()
        qs = Card.objects.filter(user=request.user, deck=deck)

        updated = 0
        for c in qs:
            c.due_at = now
            if reset:
                c.interval_days = 0.0
                c.ease = 2.3
                c.reps = 0
                c.lapses = 0
                c.avg_think_ms = None
            c.save()
            updated += 1

        return Response({"ok": True, "forced": updated, "reset_progress": reset})
