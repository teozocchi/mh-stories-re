"""Monstie scale trainer GUI.

Lets you pick your current team from the full known species list, set a size
multiplier per species, and apply it as a live drop-in edit to
nativeDX11x64\\mod\\scale\\mo\\*_body.lmt. "Apply" always starts from a clean
pristine restore, so only the species you pick end up modified -- switching
your team is just re-picking and re-applying, no manual cleanup needed.

No game assets ship with this tool. On first Apply it snapshots your CURRENT
mod\\scale\\mo files into a local scale_backup_mo/ folder -- so run it once while
your game is UNMODDED (vanilla), and that snapshot becomes the "revert" baseline.

First run: if the game's mod\\scale\\mo folder can't be found automatically, you'll
be asked to locate it once. That choice is remembered in trainer_config.json next
to this script.
"""
import json
import os
import shutil
import struct
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from species_data import build_master_list

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(SCRIPT_DIR, 'scale_backup_mo')
CONFIG_PATH = os.path.join(SCRIPT_DIR, 'trainer_config.json')
DEFAULT_MULTIPLIER = 1.5

# Common install locations to try before asking the user.
CANDIDATE_PATHS = [
    r"C:\Program Files (x86)\Steam\steamapps\common\Monster Hunter Stories\nativeDX11x64\mod\scale\mo",
    r"C:\Program Files\Steam\steamapps\common\Monster Hunter Stories\nativeDX11x64\mod\scale\mo",
    r"D:\Steam\steamapps\common\Monster Hunter Stories\nativeDX11x64\mod\scale\mo",
]


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_config(cfg):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(cfg, f, indent=2)


def resolve_game_scale_dir():
    cfg = load_config()
    saved = cfg.get('game_scale_dir')
    if saved and os.path.isdir(saved):
        return saved
    for candidate in CANDIDATE_PATHS:
        if os.path.isdir(candidate):
            cfg['game_scale_dir'] = candidate
            save_config(cfg)
            return candidate
    return None  # caller must prompt


def prompt_for_game_scale_dir():
    messagebox.showinfo(
        'Locate game folder',
        "Couldn't find the game automatically.\n\n"
        "Please select your Monster Hunter Stories install folder "
        "(the one containing nativeDX11x64)."
    )
    root_dir = filedialog.askdirectory(title='Select your Monster Hunter Stories folder')
    if not root_dir:
        return None
    scale_dir = os.path.join(root_dir, 'nativeDX11x64', 'mod', 'scale', 'mo')
    if not os.path.isdir(os.path.dirname(scale_dir)):
        # maybe they selected nativeDX11x64 itself, or the mod folder directly
        for suffix in [('mod', 'scale', 'mo'), ('scale', 'mo'), ()]:
            candidate = os.path.join(root_dir, *suffix)
            if os.path.isdir(candidate) or suffix == ():
                scale_dir = candidate if suffix else os.path.join(root_dir, 'nativeDX11x64', 'mod', 'scale', 'mo')
                break
    os.makedirs(scale_dir, exist_ok=True)
    cfg = load_config()
    cfg['game_scale_dir'] = scale_dir
    save_config(cfg)
    return scale_dir


def patch_scale(path, factor):
    with open(path, 'rb') as f:
        data = bytearray(f.read())
    if data[:4] != b'LMT\x00':
        return 0
    version, entry_count = struct.unpack_from('<HH', data, 4)
    offsets = struct.unpack_from(f'<{entry_count}Q', data, 16)
    seen_bp = set()
    n_patched = 0
    for off in offsets:
        if off == 0 or off + 96 > len(data):
            continue
        bp_off, bp_count, frame_count, loop_frame = struct.unpack_from('<Qiii', data, off)
        if bp_off == 0 or bp_off in seen_bp:
            continue
        if bp_count <= 0 or bp_count > 512:
            continue
        if bp_off + bp_count * 48 > len(data):
            continue
        seen_bp.add(bp_off)
        for i in range(bp_count):
            rec = bp_off + i * 48
            usage = data[rec + 1]
            if usage == 2:
                rx, ry, rz, rw = struct.unpack_from('<4f', data, rec + 24)
                if all(0.001 < v < 100 for v in (rx, ry, rz)):
                    struct.pack_into('<3f', data, rec + 24, rx * factor, ry * factor, rz * factor)
                    n_patched += 1
    with open(path, 'wb') as f:
        f.write(data)
    return n_patched


class TrainerApp:
    def __init__(self, root):
        self.root = root
        root.title('Monstie Scale Trainer')
        root.geometry('720x520')

        self.species = build_master_list()
        self.team = {}  # mo -> {'name': str, 'var': tk.StringVar}
        self.game_scale_dir = resolve_game_scale_dir()

        self._build_ui()

        if not self.game_scale_dir:
            self.root.after(200, self._change_game_folder)

    def _change_game_folder(self):
        chosen = prompt_for_game_scale_dir()
        if chosen:
            self.game_scale_dir = chosen
        self._update_path_label()

    def _update_path_label(self):
        text = self.game_scale_dir or '(not set -- click "Change Game Folder")'
        self.path_var.set(f'Game folder: {text}')

    def _build_ui(self):
        paned = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # left: full species list with search
        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        ttk.Label(left, text='All species (double-click to add):').pack(anchor='w')
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *a: self._refresh_species_list())
        ttk.Entry(left, textvariable=self.search_var).pack(fill=tk.X, pady=(0, 4))

        list_frame = ttk.Frame(left)
        list_frame.pack(fill=tk.BOTH, expand=True)
        self.species_list = tk.Listbox(list_frame)
        self.species_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.species_list.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.species_list.config(yscrollcommand=sb.set)
        self.species_list.bind('<Double-Button-1>', self._on_add_species)

        # right: your team
        right = ttk.Frame(paned)
        paned.add(right, weight=1)
        ttk.Label(right, text='Your team (multiplier per species):').pack(anchor='w')

        team_frame = ttk.Frame(right)
        team_frame.pack(fill=tk.BOTH, expand=True)
        self.team_canvas = tk.Canvas(team_frame, highlightthickness=0)
        self.team_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tsb = ttk.Scrollbar(team_frame, orient=tk.VERTICAL, command=self.team_canvas.yview)
        tsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.team_canvas.config(yscrollcommand=tsb.set)
        self.team_inner = ttk.Frame(self.team_canvas)
        self.team_canvas.create_window((0, 0), window=self.team_inner, anchor='nw')
        self.team_inner.bind('<Configure>', lambda e: self.team_canvas.configure(scrollregion=self.team_canvas.bbox('all')))

        # bottom controls
        bottom = ttk.Frame(self.root)
        bottom.pack(fill=tk.X, padx=8, pady=(0, 8))
        ttk.Button(bottom, text='Apply Mod', command=self._on_apply).pack(side=tk.LEFT)
        ttk.Button(bottom, text='Revert All to Vanilla', command=self._on_revert).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(bottom, text='Change Game Folder...', command=self._change_game_folder).pack(side=tk.LEFT, padx=(6, 0))
        self.status_var = tk.StringVar(value='Ready.')
        ttk.Label(self.root, textvariable=self.status_var).pack(fill=tk.X, padx=8)
        self.path_var = tk.StringVar()
        ttk.Label(self.root, textvariable=self.path_var, foreground='#666').pack(fill=tk.X, padx=8, pady=(0, 8))

        self._refresh_species_list()
        self._update_path_label()

    def _refresh_species_list(self):
        query = self.search_var.get().lower()
        self.species_list.delete(0, tk.END)
        self._visible_species = [s for s in self.species if query in s['name'].lower() or query in s['mo']]
        for s in self._visible_species:
            self.species_list.insert(tk.END, f"{s['name']}  ({s['mo']})")

    def _on_add_species(self, event):
        sel = self.species_list.curselection()
        if not sel:
            return
        s = self._visible_species[sel[0]]
        if s['mo'] in self.team:
            return
        var = tk.StringVar(value=str(DEFAULT_MULTIPLIER))
        self.team[s['mo']] = {'name': s['name'], 'var': var}
        self._rebuild_team_panel()

    def _remove_species(self, mo):
        self.team.pop(mo, None)
        self._rebuild_team_panel()

    def _rebuild_team_panel(self):
        for w in self.team_inner.winfo_children():
            w.destroy()
        for mo, info in self.team.items():
            row = ttk.Frame(self.team_inner)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=f"{info['name']} ({mo})", width=30).pack(side=tk.LEFT)
            ttk.Entry(row, textvariable=info['var'], width=6).pack(side=tk.LEFT, padx=4)
            ttk.Button(row, text='x', width=2, command=lambda m=mo: self._remove_species(m)).pack(side=tk.LEFT)

    def _ensure_backup(self):
        """Snapshot the CURRENT game files into BACKUP_DIR the first time.
        Assumes the game is vanilla at this point -- that's the revert baseline.
        Returns True if a backup exists/was created."""
        have = os.path.isdir(BACKUP_DIR) and any(os.scandir(BACKUP_DIR))
        if have:
            return True
        if not messagebox.askokcancel(
                'First-time setup',
                "No vanilla backup found yet.\n\n"
                "The tool will now snapshot your current mod\\scale\\mo files as the "
                "'revert to vanilla' baseline.\n\n"
                "Make sure the game is currently UNMODDED before continuing."):
            return False
        count = 0
        for entry in os.scandir(self.game_scale_dir):
            if not entry.is_dir():
                continue
            n = entry.name
            src = os.path.join(self.game_scale_dir, n, f'{n}_body.lmt')
            if os.path.exists(src):
                os.makedirs(os.path.join(BACKUP_DIR, n), exist_ok=True)
                shutil.copy(src, os.path.join(BACKUP_DIR, n, f'{n}_body.lmt'))
                count += 1
        self.status_var.set(f'Vanilla backup created ({count} files).')
        return count > 0

    def _restore_all_pristine(self):
        for n in os.listdir(BACKUP_DIR):
            src = os.path.join(BACKUP_DIR, n, f'{n}_body.lmt')
            dst_dir = os.path.join(self.game_scale_dir, n)
            os.makedirs(dst_dir, exist_ok=True)
            dst = os.path.join(dst_dir, f'{n}_body.lmt')
            if os.path.exists(src):
                shutil.copy(src, dst)

    def _on_apply(self):
        if not self.game_scale_dir or not os.path.isdir(os.path.dirname(self.game_scale_dir)):
            messagebox.showerror('Error', 'Game folder not set. Click "Change Game Folder..." first.')
            return
        try:
            if not self._ensure_backup():
                return
            self._restore_all_pristine()
            applied = []
            for mo, info in self.team.items():
                try:
                    factor = float(info['var'].get())
                except ValueError:
                    messagebox.showerror('Error', f"Invalid multiplier for {info['name']}: {info['var'].get()!r}")
                    return
                dst = os.path.join(self.game_scale_dir, mo, f'{mo}_body.lmt')
                if not os.path.exists(dst):
                    messagebox.showwarning('Warning', f'{mo} not found in game folder, skipped.')
                    continue
                patch_scale(dst, factor)
                applied.append(f"{info['name']} x{factor}")
            self.status_var.set('Applied: ' + (', '.join(applied) if applied else 'nothing selected, all vanilla'))
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def _on_revert(self):
        if not (os.path.isdir(BACKUP_DIR) and any(os.scandir(BACKUP_DIR))):
            messagebox.showinfo(
                'No backup yet',
                "No vanilla backup exists to revert to. A backup is created the "
                "first time you click Apply (while the game is unmodded).")
            return
        try:
            self._restore_all_pristine()
            self.status_var.set('All species reverted to vanilla.')
        except Exception as e:
            messagebox.showerror('Error', str(e))


if __name__ == '__main__':
    root = tk.Tk()
    app = TrainerApp(root)
    root.mainloop()
