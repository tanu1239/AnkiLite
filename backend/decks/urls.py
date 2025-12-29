from django.urls import path
from .views import DecksView, DeckDetailView, DeckCardsView, ForceDueView

urlpatterns = [
    path("decks/", DecksView.as_view()),                         # /api/decks/
    path("decks/<int:deck_id>/", DeckDetailView.as_view()),      # /api/decks/:id/
    path("decks/<int:deck_id>/cards/", DeckCardsView.as_view()), # /api/decks/:id/cards/
    path("decks/<int:deck_id>/force_due/", ForceDueView.as_view()) # /api/decks/:id/force_due/
]
