"""Approximate IELTS Academic Reading band from raw score (40-question scale)."""

# Official-style conversion table (raw correct -> band)
READING_BAND_TABLE_40 = [
    (39, 9.0),
    (37, 8.5),
    (35, 8.0),
    (33, 7.5),
    (30, 7.0),
    (27, 6.5),
    (23, 6.0),
    (19, 5.5),
    (15, 5.0),
    (13, 4.5),
    (10, 4.0),
    (8, 3.5),
    (6, 3.0),
    (4, 2.5),
    (0, 0.0),
]


def reading_band_from_raw(correct: int, total: int = 40) -> float:
    """Map correct answers to band score; scales if total != 40."""
    if total <= 0:
        return 0.0
    scaled = round(40 * correct / total)
    scaled = max(0, min(40, scaled))
    for threshold, band in READING_BAND_TABLE_40:
        if scaled >= threshold:
            return band
    return 0.0
