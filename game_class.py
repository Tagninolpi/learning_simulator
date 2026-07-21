import json
import random

class Game:
    def __init__(self):
        with open("words.json", encoding="utf-8") as f:
            raw = json.load(f)

        # expand: {"あう": ["treffen", "begegnen"]} → [("あう", "treffen"), ("あう", "begegnen")]
        self.all_words = []
        for japanese, translations in raw.items():
            for translation in translations:
                self.all_words.append((japanese.strip(), translation.strip()))

        self.active_words = []
        self.remaining = []
        self.wrong_words = []
        self.current_word = None
        self.last_word = None

    def get_word_groups(self) -> list:
        groups = []
        for i in range(0, len(self.all_words), 25):
            chunk = self.all_words[i:i+25]
            groups.append({
                "group_index": i // 25,
                "words": [{"japanese": jp, "german": de} for jp, de in chunk]
            })
        return groups

    def set_active_words_from_groups(self, selected_group_indices: list):
        selected = []
        for gi in selected_group_indices:
            start = gi * 25
            selected.extend(self.all_words[start:start+25])
        self.active_words = selected
        self.remaining = list(self.active_words)
        self.wrong_words = []
        self.current_word = None
        self.last_word = None

    def next_question(self):
        if not self.remaining:
            if not self.wrong_words:
                return None
            self.remaining = list(self.wrong_words)
            self.wrong_words = []

        self.current_word = random.choice(self.remaining)

        wrong_pool = [w for w in self.active_words if w != self.current_word]
        wrong_answers = random.sample(wrong_pool, min(4, len(wrong_pool)))
        while len(wrong_answers) < 4:
            wrong_answers.append(("？", "???"))

        buttons = wrong_answers + [self.current_word]
        random.shuffle(buttons)

        return {
            "japanese": self.current_word[0],
            "buttons": [
                {"german": w[1], "correct": w == self.current_word}
                for w in buttons
            ],
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
        self.remaining.remove(self.current_word)
        if not was_correct and self.current_word not in self.wrong_words:
            self.wrong_words.append(self.current_word)
        self.current_word = None
    
    def set_active_words_from_indices(self, selected_indices: list):
        self.active_words = [self.all_words[i] for i in selected_indices if i < len(self.all_words)]
        self.remaining = list(self.active_words)
        self.wrong_words = []
        self.current_word = None
        self.last_word = None