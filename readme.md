# 🗒️ Freak Notepad

> *Ini bukan notepad biasa.*

Proyek akhir mata kuliah **Pemrograman Berorientasi Objek**  
Semester 2 — Program Studi Teknologi Rekayasa Internet

---

## 📋 Deskripsi

**Freak Notepad** adalah game berbasis Python/Pygame dengan premis sederhana: pemain membuka sebuah aplikasi yang terlihat persis seperti Notepad biasa. Tidak ada petunjuk. Tidak ada instruksi. Hanya sebuah teks editor kosong.

Namun seiring waktu, notepad mulai *berperilaku aneh*.

Karakter-karakter di layar mulai bergeser sendiri. Menu bar berubah. Frame aplikasi mulai retak. Dan sebelum pemain menyadarinya, mereka sudah berada di tengah-tengah sebuah game yang semakin absurd — semuanya terjadi di dalam jendela notepad yang sama.

---

## 🎮 Cara Bermain

```bash
# Clone / download project
cd freak_notepad

# Install dependency
pip install pygame

# Jalankan
python3 main.py
```

| Kontrol | Fungsi |
|---------|--------|
| Keyboard | Mengetik di notepad / interaksi stage |
| Mouse | Klik tombol, hindari lingkaran |
| `R` | Restart dari awal |
| `ESC` | Keluar |

---

## 🗺️ Alur Game

```
Buka aplikasi
     │
     ▼
[FASE NOTEPAD]  ← Terlihat seperti text editor biasa
 ~8 detik tenang, lalu glitch mulai muncul subtle
     │
     ▼ (18 detik)
[STAGE 1] Red Circle Chasing Cursor
     │  Survive tanpa ketangkap selama 14 detik
     ▼
[STAGE 2] Self-Aware Calculator
     │  Tekan '=' sebanyak 5 kali
     ▼
[STAGE 3] Broken Calculator
     │  Temukan dan klik tombol '=' di antara tombol-tombol acak
     ▼
[STAGE 4] Teleporting Button
     │  Klik tombol yang selalu kabur sebanyak 3 kali
     ▼
[STAGE 5] Shy Buttons
     │  Klik semua 12 tombol yang malu-malu
     ▼
[STAGE 6] Screaming Notepad
     │  Ketik kata "SORRY" untuk menenangkan notepad
     ▼
[STAGE 7] Gravity Calculator
     │  Klik '=' 3 kali sebelum semua tombol jatuh ke lantai
     ▼
[YOU SURVIVED!]
```

> ⚠️ **Gagal = Game Over**, harus restart dari awal.

---

## 🏗️ Arsitektur — MVC Pattern

Project ini menerapkan pola arsitektur **Model-View-Controller (MVC)** secara konsisten.

```
freak_notepad/
├── main.py                         # Entry point
└── src/
    ├── models/                     # DATA — tidak ada logika UI
    │   ├── game_state.py           # Phase, stage index, glitch level
    │   ├── notepad_model.py        # Teks, cursor, glitch chars
    │   └── stage_model.py          # Timer, done/failed, data bag per stage
    │
    ├── views/                      # TAMPILAN — hanya membaca data, tidak mengubah
    │   ├── base_view.py            # Konstanta warna, font, helper drawing
    │   ├── notepad_view.py         # Shell notepad (title bar, toolbar, status bar)
    │   ├── hud_view.py             # Timer bar, label stage
    │   └── stages/
    │       └── stage_views.py      # 7 view terpisah per stage
    │
    ├── controllers/                # LOGIKA — update model, handle input
    │   ├── input_controller.py     # Centralized pygame event pump
    │   ├── notepad_controller.py   # Logika fase notepad & glitch
    │   ├── game_controller.py      # Orchestrator utama (game loop)
    │   └── stages/
    │       └── stage_controllers.py # 7 controller terpisah per stage
    │
    └── utils/
        ├── sfx.py                  # Sound effects procedural (tanpa file audio)
        └── transitions.py         # Animasi Win / Game Over / Transisi stage
```

### Pembagian Tanggung Jawab

| Layer | Tanggung Jawab | Contoh |
|-------|---------------|--------|
| **Model** | Menyimpan state, tidak tahu soal rendering | `GameState.phase`, `StageModel.elapsed` |
| **View** | Membaca model, menggambar ke surface | `NotepadView.draw_stage_shell()` |
| **Controller** | Menerima input, mengubah model | `RedCircleController.update()` |

---

## 🧩 Konsep OOP yang Diterapkan

### 1. Encapsulation
Setiap class menyembunyikan detail implementasinya. `NotepadModel` mengelola teks buffer secara internal — controller cukup memanggil `insert_char()` atau `backspace()` tanpa tahu cara kerjanya.

```python
class NotepadModel:
    def insert_char(self, ch: str):
        line = self.lines[self.cursor_line]
        self.lines[self.cursor_line] = (
            line[:self.cursor_col] + ch + line[self.cursor_col:]
        )
        self.cursor_col += 1
```

### 2. Inheritance
`StageModel` adalah dataclass tunggal yang digunakan oleh semua 7 stage — tiap stage controller membuat instance-nya dengan parameter berbeda tanpa perlu subclass.

### 3. Polymorphism
Semua stage controller dan view mengikuti interface yang sama: `update(dt, events, mouse)` dan `draw(surf, model, stage_model)`. `GameController` bisa memanggil keduanya tanpa tahu stage mana yang sedang aktif.

```python
# GameController tidak perlu tahu ini stage apa
self.stage_ctrl.update(dt, events, mouse)
self.stage_view.draw(self.screen, self.nm, self.stage_ctrl.model)
```

### 4. Abstraction
`SFX` menggunakan metaclass `_SFXMeta` untuk lazy initialization — sound hanya dibuat saat pertama kali diakses, memastikan `pygame.mixer` sudah terinisialisasi.

```python
class _SFXMeta(type):
    def __getattr__(cls, name):
        if name in cls._recipes:
            if name not in cls._cache:
                cls._cache[name] = cls._recipes[name]()
            return cls._cache[name]
```

### 5. Separation of Concerns
Tidak ada cross-dependency antar layer:
- Model tidak mengimport pygame
- View tidak mengubah model
- Controller tidak merender langsung ke layar

---

## ⚙️ Teknologi

| Library | Versi | Kegunaan |
|---------|-------|----------|
| Python  | 3.10+ | Bahasa utama |
| Pygame  | 2.x   | Rendering, input, audio |

Tidak ada dependency eksternal lain. Sound effects dibuat secara **prosedural** menggunakan sine wave dan noise — tidak memerlukan file `.wav` atau `.mp3`.

---

## 👥 Tim

| Nama | NIM | Kontribusi |
|------|-----|-----------|
|  |  |  |

---

## 📄 Lisensi

Proyek ini dibuat untuk keperluan akademik.  
Program Studi Teknologi Rekayasa Internet — Semester 2.