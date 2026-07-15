english_rules = {
    # --------------------------------------------------
    # ENGLISH-SPECIFIC BRIDGE RULES & EXCEPTIONS
    # Only the weird stuff that common_rules doesn't catch
    # --------------------------------------------------
    
    # R-colored vowels and specific English R clusters
    "t͡ʃəɹ": ["チャー"], "sɛɹ": ["サラ"], 
    "əɹ": ["ー"], "ɚ": ["ー"], "ɝ": ["ー"],
    "ɹɪ": ["リ"], "ɹeɪ": ["レイ"], "ɹə": ["ラ"], "ɹɑ": ["ラ"], "ɹoʊ": ["ロ"],

    # Common English specific clusters
    "mæ": ["マ"], "θjuː": ["テュー"],
    "sæ": ["サ"], "sɛ": ["セ"], "sɪ": ["シ"], "soʊ": ["ソ"], "su": ["ス"], "sə": ["サ"],
    "tɪ": ["ティ"], "tæ": ["タ"], "tu": ["トゥ"], "tə": ["タ"],
    
    # Affricate English clusters (Ch, J, Sh)
    "t͡ʃæ": ["チャ"], "t͡ʃə": ["チャ"], "t͡ʃɪ": ["チ"], "t͡ʃi": ["チ"],
    "θj": ["シュ"], "θə": ["サ"], "ðə": ["ザ"],

    # --------------------------------------------------
    # CUSTOM NAME FIXES (The "Human Filter")
    # --------------------------------------------------
    "hɑːr": ["ハー"],  # Harleigh -> ハーリー 
    "liː": ["リー"],   # Shirlee -> シャーリー 
    "drə": ["ドラ"],   # Alexandra -> アレクサンドラ 
    "dɛ": ["デ"],      # Debbi -> デビー
    "mɜː": ["マー"],   # Merletta -> マールエッタ
    
    # Conflict Resolution: 
    # 'mə' can be 'マ' (Malaysia) or 'メ' (Melina). 
    # We will default to 'マ' here, but add 'məl' for Melina.
    "mə": ["マ"],         
    "məliː": ["メリー"], # Melina -> メリーナ
    "ʒə": ["ーシャ"],    
}