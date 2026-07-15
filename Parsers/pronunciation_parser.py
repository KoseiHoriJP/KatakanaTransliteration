def parse_pronunciation(pronunciation):
    if not pronunciation or not isinstance(pronunciation, str):
        return {
            "syllables": [],
            "num_syllables": 0,
            "stress_position": None
        }

    # Split and strip white space
    syllables = [s.strip() for s in pronunciation.split("-")]

    # Find syllables that are uppercase AND contain letters (the stress)
    stress_positions = [
        idx
        for idx, syllable in enumerate(syllables)
        if syllable.isupper() and any(c.isalpha() for c in syllable)
    ]

    stress_position = (
        stress_positions[0]
        if len(stress_positions) > 0
        else None
    )

    return {
        "syllables": syllables,
        "num_syllables": len(syllables),
        "stress_position": stress_position
    }