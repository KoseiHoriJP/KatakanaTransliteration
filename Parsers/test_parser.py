import sys
import os

# 1. Get the directory of the current script (Parsers/)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Get the Parent Directory (The project root)
# This is where your 'Rules/' folder lives!
parent_dir = os.path.dirname(current_dir)

# 3. Add the project root to the system path
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Now we can import the modules
from ipa_parser import ipa_parser

# List your problem names here
test_cases = [
    {"ipa": "ɹɪt͡ʃ.əˈdiːn", "name": "Richardine"},
    {"ipa": "ˈdɛb.i",       "name": "Debbi"},
    {"ipa": "ˈʃɜː.li",      "name": "Shirlee"},
    {"ipa": "mɜː.ˈlɛt.ə",   "name": "Merletta"},
    {"ipa": "ˌæl.ɪɡˈzɑːn.drə", "name": "Alexandra"},
    {"ipa": "mə.ˈliː.nə",   "name": "Melina"},
    {"ipa": "mə.ˈleɪ.ʒə",   "name": "Malaysia"},
    {"ipa": "ˈhɑːr.li",     "name": "Harleigh"}
]

for case in test_cases:
    # Run the parser
    result = ipa_parser(case["ipa"], "english")
    print(f"Name: {case['name']}")
    print(f"IPA:  {case['ipa']}")
    print(f"Result: {result['katakana_string']}")
    print("-" * 20)