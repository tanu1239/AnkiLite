from django.urls import path
from .views import DueCardsView, ReviewCardView, CramCardsView

urlpatterns = [
    path("review/due", DueCardsView.as_view()),
    path("review/cram", CramCardsView.as_view()),
    path("review/<int:card_id>", ReviewCardView.as_view()),
]
