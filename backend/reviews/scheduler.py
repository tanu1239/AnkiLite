from datetime import timedelta

def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def update_avg(old, new, alpha=0.2):
    if new is None:
        return old
    if old is None:
        return int(new)
    return int(round((1 - alpha) * old + alpha * new))


def latency_bonus_multiplier(avg_think_ms: int | None, think_ms: int | None) -> float:
    """
    Slightly reward faster-than-usual recall; slightly punish slower-than-usual recall.
    Keep it gentle.
    """
    if think_ms is None:
        return 1.0
    if avg_think_ms is None or avg_think_ms <= 0:
        return 1.0

    ratio = think_ms / avg_think_ms
    # faster -> <1; slower -> >1
    if ratio <= 0:
        return 1.0

    # gentle: +/- up to ~10%
    if ratio < 0.75:
        return 1.08
    if ratio < 0.9:
        return 1.04
    if ratio > 1.5:
        return 0.92
    if ratio > 1.2:
        return 0.96
    return 1.0


def apply_review(card, grade: int, think_ms: int | None, now):
    """
    grade: 0 Again, 1 Hard, 2 Good, 3 Easy
    - fixed: due_at = now + deck's chosen duration for that grade
    - hybrid:
        * early reps (<2): use deck durations as learning steps
        * later: grow interval_days using ease and multipliers
    """
    deck = card.deck

    # record latency average
    card.avg_think_ms = update_avg(card.avg_think_ms, think_ms)

    # map grade to deck minutes
    grade_to_minutes = {
        0: deck.again_minutes,
        1: deck.hard_minutes,
        2: deck.good_minutes,
        3: deck.easy_minutes,
    }

    grade = int(grade)
    if grade not in {0, 1, 2, 3}:
        grade = 2

    # FIXED MODE: literal timers always
    if deck.schedule_mode == "fixed":
        mins = grade_to_minutes[grade]
        card.due_at = now + timedelta(minutes=mins)
        # still track progress lightly (optional), but don't “grow”
        if grade == 0:
            card.lapses += 1
        else:
            card.reps += 1
        return

    # HYBRID MODE
    # Learning phase (first 2 successful reps): same as fixed timers
    if card.reps < 2:
        if grade == 0:
            card.lapses += 1
            card.ease = clamp(card.ease - 0.2, 1.3, 3.0)
        else:
            card.reps += 1
            if grade == 1:
                card.ease = clamp(card.ease - 0.15, 1.3, 3.0)
            elif grade == 3:
                card.ease = clamp(card.ease + 0.1, 1.3, 3.0)

        mins = grade_to_minutes[grade]
        card.due_at = now + timedelta(minutes=mins)
        return

    # Spaced phase: grow interval_days
    bonus = latency_bonus_multiplier(card.avg_think_ms, think_ms)

    if grade == 0:
        # Again: quick relearn step
        card.lapses += 1
        card.ease = clamp(card.ease - 0.2, 1.3, 3.0)
        # relearn step uses deck again timer
        card.due_at = now + timedelta(minutes=deck.again_minutes)
        # optionally reduce interval a bit
        card.interval_days = max(0.0, card.interval_days * 0.5)
        return

    # hard/good/easy increase interval
    if card.interval_days < 1.0:
        card.interval_days = 1.0

    if grade == 1:
        # Hard: modest growth
        card.ease = clamp(card.ease - 0.05, 1.3, 3.0)
        card.interval_days = card.interval_days * 1.2 * bonus
    elif grade == 2:
        # Good: standard growth by ease
        card.interval_days = card.interval_days * card.ease * bonus
    else:
        # Easy: slightly more than Good
        card.ease = clamp(card.ease + 0.1, 1.3, 3.0)
        card.interval_days = card.interval_days * (card.ease + 0.3) * bonus

    card.interval_days = clamp(card.interval_days, 1.0, 3650.0)
    card.reps += 1
    card.due_at = now + timedelta(days=float(card.interval_days))


def priority_score(card, now):
    """
    Score due cards for ordering within a session.
    Higher = show sooner.
    """
    # overdue minutes
    overdue = max(0.0, (now - card.due_at).total_seconds() / 60.0)

    # shorter-think cards can be queued later (they're easier)
    think = card.avg_think_ms if card.avg_think_ms is not None else 3000

    return overdue - (think / 1000.0) * 0.1
