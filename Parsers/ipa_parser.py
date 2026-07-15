from Rules.common_rules import common_rules
from Rules.english_rules import english_rules
from Rules.french_rules import french_rules

def get_rules(language):
    rules = {}
    rules.update(common_rules)

    lang_lower = language.lower()
    if "english" in lang_lower:
        rules.update(english_rules)
    elif "french" in lang_lower:
        rules.update(french_rules)

    return rules

def ipa_parser(ipa, language, pron_hint="", is_stressed=False):
    rules = get_rules(language)

    # Greedy match: sort keys by length descending
    keys = sorted(rules.keys(), key=len, reverse=True)

    result = []
    phonemes = []
    unmatched = []

    i = 0
    pron_hint_lower = pron_hint.lower()

    while i < len(ipa):
        matched = False

        for key in keys:
            if ipa[i:].startswith(key):
                value_list = rules[key]

                if isinstance(value_list, list):
                    # Smart Schwa overrides based on spelling
                    if key in ["ə", "əɹ", "ɚ", "ɝ"] and pron_hint_lower:
                        if "a" in pron_hint_lower: value = "ア"
                        elif "o" in pron_hint_lower: value = "オ"
                        elif "e" in pron_hint_lower: value = "エ"
                        elif "i" in pron_hint_lower: value = "イ"
                        elif "u" in pron_hint_lower: value = "ウ"
                        else: value = value_list[0]
                    else:
                        value = value_list[0] 
                else:
                    value = value_list

                result.append(value)
                phonemes.append(key)
                i += len(key)
                matched = True
                break

        if not matched:
            unmatched.append(ipa[i])
            i += 1

    katakana_string = "".join(result)

    # Smart Stress Elongation
    if is_stressed and katakana_string:
        if not katakana_string.endswith("ー") and not katakana_string.endswith("ン") and not katakana_string.endswith("ッ"):
            katakana_string += "ー"
            result.append("ー") 

    return {
        "phonemes": phonemes,
        "katakana_parts": result,
        "katakana_string": katakana_string,
        "unmatched": unmatched
    }