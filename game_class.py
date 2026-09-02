import json
import random
import time
import os

class Game:
    def __init__(self):
        # --- Japanese ---
        with open("words.json", encoding="utf-8") as f:
            raw = json.load(f)
        self.all_words = []
        for japanese, translations in raw.items():
            for translation in translations:
                self.all_words.append((japanese.strip(), translation.strip()))

        # --- Marines ---
        marines_path = "static/images/marines"
        self.all_grades = []
        if os.path.exists(marines_path):
            for fname in sorted(os.listdir(marines_path)):
                if fname.lower().endswith(".png"):
                    name = fname[:-4]  # strip .png
                    self.all_grades.append({
                        "name": name,
                        "path": f"/static/images/marines/{fname}"
                    })

        # --- Shared game state ---
        self.active_words = []
        self.remaining = []
        self.wrong_words = []
        self.current_word = None
        self.last_word = None
        self.mode = None  # "japanese", "marines_image", "marines_word"

        # --- Stats ---
        self.stats = {}       # { word/name: { attempts, wrong, start_time, total_time } }
        self.game_start = None

    # ── Japanese helpers ──────────────────────────────────────────────

    def get_word_list(self) -> list:
        return [{"japanese": jp, "german": de} for jp, de in self.all_words]

    def set_active_words_from_indices(self, selected_indices: list):
        self.active_words = [self.all_words[i] for i in selected_indices if i < len(self.all_words)]
        self._init_round("japanese")

    # ── Marines helpers ───────────────────────────────────────────────

    def set_active_grades(self, mode: str):
        # mode: "marines_image" or "marines_word"
        self.active_words = list(self.all_grades)
        self._init_round(mode)

    # ── Shared init ───────────────────────────────────────────────────

    def _init_round(self, mode: str):
        self.mode = mode
        self.remaining = list(self.active_words)
        self.wrong_words = []
        self.current_word = None
        self.last_word = None
        self.game_start = time.time()
        self.stats = {
            self._word_key(w): {"attempts": 0, "wrong": 0, "first_seen": None, "total_time": 0}
            for w in self.active_words
        }

    def _word_key(self, w):
        if isinstance(w, tuple):
            return f"{w[0]}|{w[1]}"
        return w["name"]

    # ── Next question ─────────────────────────────────────────────────

    def next_question(self):
        if not self.remaining:
            if not self.wrong_words:
                return None  # game over
            self.remaining = list(self.wrong_words)
            self.wrong_words = []

        self.current_word = random.choice(self.remaining)
        key = self._word_key(self.current_word)
        self.stats[key]["attempts"] += 1
        self.stats[key]["first_seen"] = self.stats[key]["first_seen"] or time.time()
        self._question_start = time.time()

        if self.mode == "japanese":
            return self._japanese_question()
        elif self.mode == "marines_image":
            return self._marines_image_question()
        elif self.mode == "marines_word":
            return self._marines_word_question()

    def _japanese_question(self):
        correct = self.current_word
        # exclude words with same japanese as correct (avoids ambiguous choices)
        wrong_pool = [w for w in self.active_words
                      if w != correct and w[0] != correct[0]]
        wrong_answers = random.sample(wrong_pool, min(4, len(wrong_pool)))
        while len(wrong_answers) < 4:
            wrong_answers.append(("？", "???"))
        buttons = wrong_answers + [correct]
        random.shuffle(buttons)
        return {
            "mode": "japanese",
            "japanese": correct[0],
            "buttons": [{"german": w[1], "correct": w == correct} for w in buttons],
            "last_word": self._last_word_payload()
        }

    def _marines_image_question(self):
        # show the word, pick 4 wrong images + 1 correct image
        correct = self.current_word
        wrong_pool = [w for w in self.active_words if w["name"] != correct["name"]]
        wrong_answers = random.sample(wrong_pool, min(3, len(wrong_pool)))
        choices = wrong_answers + [correct]
        random.shuffle(choices)
        return {
            "mode": "marines_image",
            "word": correct["name"],
            "choices": [{"path": w["path"], "name": w["name"], "correct": w["name"] == correct["name"]} for w in choices],
            "last_word": self._last_word_payload()
        }

    def _marines_word_question(self):
        # show the image, pick 4 wrong words + 1 correct word
        correct = self.current_word
        wrong_pool = [w for w in self.active_words if w["name"] != correct["name"]]
        wrong_answers = random.sample(wrong_pool, min(4, len(wrong_pool)))
        while len(wrong_answers) < 4:
            wrong_answers.append({"name": "???", "path": ""})
        buttons = wrong_answers + [correct]
        random.shuffle(buttons)
        return {
            "mode": "marines_word",
            "image": correct["path"],
            "buttons": [{"name": w["name"], "correct": w["name"] == correct["name"]} for w in buttons],
            "last_word": self._last_word_payload()
        }

    def _last_word_payload(self):
        if not self.last_word:
            return None
        w = self.last_word
        if self.mode == "japanese":
            return {"japanese": w[0], "german": w[1], "correct": w[2]}
        else:
            return {"name": w[0], "path": w[1], "correct": w[2]}

    # ── Answer ────────────────────────────────────────────────────────

    def answer(self, was_correct: bool):
        if self.current_word is None:
            return
        elapsed = time.time() - self._question_start
        key = self._word_key(self.current_word)
        self.stats[key]["total_time"] += elapsed
        if not was_correct:
            self.stats[key]["wrong"] += 1

        if self.mode == "japanese":
            self.last_word = (self.current_word[0], self.current_word[1], was_correct)
        else:
            self.last_word = (self.current_word["name"], self.current_word["path"], was_correct)

        self.remaining.remove(self.current_word)
        if not was_correct and self.current_word not in self.wrong_words:
            self.wrong_words.append(self.current_word)
        self.current_word = None

    # ── Stats ─────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        total_time = time.time() - self.game_start
        rows = []
        for w in self.active_words:
            key = self._word_key(w)
            s = self.stats[key]
            label = f"{w[0]} / {w[1]}" if isinstance(w, tuple) else w["name"]
            rows.append({
                "word": label,
                "attempts": s["attempts"],
                "wrong": s["wrong"],
                "time": round(s["total_time"], 1)
            })
        rows.sort(key=lambda r: (r["wrong"], r["time"]), reverse=True)
        accuracy = sum(1 for r in rows if r["wrong"] == 0) / len(rows) * 100 if rows else 0
        fastest = min(rows, key=lambda r: r["time"]) if rows else None
        slowest = max(rows, key=lambda r: r["time"]) if rows else None
        return {
            "total_time": round(total_time, 1),
            "accuracy": round(accuracy, 1),
            "fastest": fastest,
            "slowest": slowest,
            "rows": rows
        }