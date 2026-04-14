import random
class Game:
    def __init__(self):
        self.hiragana = {
    # Simple vowels
    "a": "あ", "i": "い", "u": "う", "e": "え", "o": "お",

    # K row
    "ka": "か", "ki": "き", "ku": "く", "ke": "け", "ko": "こ",

    # S row
    "sa": "さ", "shi": "し", "su": "す", "se": "せ", "so": "そ",

    # T row
    "ta": "た", "chi": "ち", "tsu": "つ", "te": "て", "to": "と",

    # N row
    "na": "な", "ni": "に", "nu": "ぬ", "ne": "ね", "no": "の",

    # H row
    "ha": "は", "hi": "ひ", "fu": "ふ", "he": "へ", "ho": "ほ",

    # M row
    "ma": "ま", "mi": "み", "mu": "む", "me": "め", "mo": "も",

    # Y row
    "ya": "や", "yu": "ゆ", "yo": "よ",

    # R row
    "ra": "ら", "ri": "り", "ru": "る", "re": "れ", "ro": "ろ",

    # W row
    "wa": "わ", "wi": "ゐ", "we": "ゑ", "wo": "を",

    # N alone
    "n": "ん",

    # G row — voiced (dakuten ゛)
    "ga": "が", "gi": "ぎ", "gu": "ぐ", "ge": "げ", "go": "ご",

    # Z row — voiced
    "za": "ざ", "ji": "じ", "zu": "ず", "ze": "ぜ", "zo": "ぞ",

    # D row — voiced
    "da": "だ", "di": "ぢ", "du": "づ", "de": "で", "do": "ど",

    # B row — voiced
    "ba": "ば", "bi": "び", "bu": "ぶ", "be": "べ", "bo": "ぼ",

    # P row — half-voiced (handakuten ゜)
    "pa": "ぱ", "pi": "ぴ", "pu": "ぷ", "pe": "ぺ", "po": "ぽ",

    # KY combination row
    "kya": "きゃ", "kyu": "きゅ", "kyo": "きょ",

    # SH combination row
    "sha": "しゃ", "shu": "しゅ", "sho": "しょ",

    # CH combination row
    "cha": "ちゃ", "chu": "ちゅ", "cho": "ちょ",

    # NY combination row
    "nya": "にゃ", "nyu": "にゅ", "nyo": "にょ",

    # HY combination row
    "hya": "ひゃ", "hyu": "ひゅ", "hyo": "ひょ",

    # MY combination row
    "mya": "みゃ", "myu": "みゅ", "myo": "みょ",

    # RY combination row
    "rya": "りゃ", "ryu": "りゅ", "ryo": "りょ",

    # GY combination row — voiced
    "gya": "ぎゃ", "gyu": "ぎゅ", "gyo": "ぎょ",

    # JY combination row — voiced
    "ja": "じゃ", "ju": "じゅ", "jo": "じょ",

    # BY combination row — voiced
    "bya": "びゃ", "byu": "びゅ", "byo": "びょ",

    # PY combination row — half-voiced
    "pya": "ぴゃ", "pyu": "ぴゅ", "pyo": "ぴょ",
}
        
        self.all_words_latin = {
            "au": "treffen", "aida": "zwischen", "aku": "öffnen",
            "ageru": "geben", "aji": "Geschmack", "asa": "morgen",
            "asobu": "spielen", "atsumaru": "sammeln", "ayamaru": "sich entschuldigen",
            "anshin": "Beruhigung", "anzen": "Sicherheit", "annai suru": "führen",
            "ika": "unterhalb", "igai": "ausser", "ikiru": "leben",
            "iken": "Meinung", "ijimeru": "ärgern", "isogu": "sich beeilen",
            "ijou": "übersteigend",
        }
        self.all_words = self._convert_words()
        self.active_words = []      # full pool for wrong answers, set once
        self.remaining = []         # words still to guess this round
        self.wrong_words = []       # words guessed incorrectly
        self.current_word = None    # (japanese, german) currently shown
        self.last_word = None       # (japanese, german, was_correct) for bottom display


    def _latin_to_hiragana(self, latin: str) -> str:
        # Sort keys longest first to match multi-char combos before single chars
        sorted_keys = sorted(self.hiragana.keys(), key=len, reverse=True)
        result = ""
        i = 0
        while i < len(latin):
            matched = False
            for key in sorted_keys:
                if latin[i:i+len(key)] == key:
                    result += self.hiragana[key]
                    i += len(key)
                    matched = True
                    break
            if not matched:
                result += latin[i]  # keep character as-is if no match (e.g. space)
                i += 1
        return result

    def _convert_words(self) -> dict:
        # Returns { "hiragana": "german", ... }
        return {
            self._latin_to_hiragana(latin): german
            for latin, german in self.all_words_latin.items()
        }

    def set_active_words(self, selected_indices: list):
        items = list(self.all_words.items())
        self.active_words = [items[i] for i in selected_indices if i < len(items)]
    
    def set_active_words(self, selected_indices: list):
        items = list(self.all_words.items())
        self.active_words = [items[i] for i in selected_indices if i < len(items)]
        self.remaining = list(self.active_words)
        self.wrong_words = []
        self.current_word = None
        self.last_word = None

    def next_question(self):
        # if remaining is empty, refill from wrong words or signal completion
        if not self.remaining:
            if not self.wrong_words:
                return None  # all done — signal game over
            self.remaining = list(self.wrong_words)
            self.wrong_words = []

        # pick a random word to guess
        self.current_word = random.choice(self.remaining)

        # pick 4 wrong answers from active_words excluding the correct one
        wrong_pool = [w for w in self.active_words if w != self.current_word]
        wrong_answers = random.sample(wrong_pool, min(4, len(wrong_pool)))

        # if not enough unique wrong answers, pad with placeholders
        while len(wrong_answers) < 4:
            wrong_answers.append(("？", "???"))

        # build shuffled button list: 1 correct + 4 wrong
        buttons = wrong_answers + [self.current_word]
        random.shuffle(buttons)

        return {
            "japanese": self.current_word[0],
            "buttons": [{"german": w[1], "correct": w == self.current_word} for w in buttons],
            "last_word": {
                "japanese": self.last_word[0],
                "german": self.last_word[1],
                "correct": self.last_word[2]
            } if self.last_word else None
        }

    def answer(self, was_correct: bool):
        if self.current_word is None:
            return
        self.last_word = (self.current_word[0], self.current_word[1], was_correct)
        if was_correct:
            self.remaining.remove(self.current_word)
        else:
            self.remaining.remove(self.current_word)
            if self.current_word not in self.wrong_words:
                self.wrong_words.append(self.current_word)
        self.current_word = None
