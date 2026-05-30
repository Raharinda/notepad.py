"""
models/notepad_model.py
Holds the text content, cursor position, and subtle glitch state
for the "fake notepad" phase.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class NotepadModel:
    lines:          List[str] = field(default_factory=lambda: [""])
    cursor_line:    int       = 0
    cursor_col:     int       = 0
    glitch_chars:   List      = field(default_factory=list)   # [(line,col,char,life)]
    scroll_offset:  int       = 0   # first visible line index
    max_visible:    int       = 18

    # ── Text editing ──────────────────────────────────────────────────────
    def insert_char(self, ch: str):
        line = self.lines[self.cursor_line]
        self.lines[self.cursor_line] = (
            line[:self.cursor_col] + ch + line[self.cursor_col:]
        )
        self.cursor_col += 1

    def backspace(self):
        if self.cursor_col > 0:
            line = self.lines[self.cursor_line]
            self.lines[self.cursor_line] = (
                line[:self.cursor_col - 1] + line[self.cursor_col:]
            )
            self.cursor_col -= 1
        elif self.cursor_line > 0:
            prev = self.lines[self.cursor_line - 1]
            self.cursor_col = len(prev)
            self.lines[self.cursor_line - 1] = prev + self.lines[self.cursor_line]
            self.lines.pop(self.cursor_line)
            self.cursor_line -= 1

    def newline(self):
        line = self.lines[self.cursor_line]
        rest = line[self.cursor_col:]
        self.lines[self.cursor_line] = line[:self.cursor_col]
        self.lines.insert(self.cursor_line + 1, rest)
        self.cursor_line += 1
        self.cursor_col   = 0

    def move_cursor(self, dx: int, dy: int):
        self.cursor_line = max(0, min(len(self.lines)-1, self.cursor_line + dy))
        self.cursor_col  = max(0, min(len(self.lines[self.cursor_line]),
                                      self.cursor_col + dx))

    # ── Glitch helpers ────────────────────────────────────────────────────
    def add_glitch_char(self, line: int, col: int, ch: str, life: float = 1.5):
        self.glitch_chars.append([line, col, ch, life])

    def update_glitches(self, dt: float):
        for g in self.glitch_chars:
            g[3] -= dt
        self.glitch_chars = [g for g in self.glitch_chars if g[3] > 0]

    def full_text(self) -> str:
        return "\n".join(self.lines)

    def reset(self):
        self.lines         = [""]
        self.cursor_line   = 0
        self.cursor_col    = 0
        self.glitch_chars  = []
        self.scroll_offset = 0