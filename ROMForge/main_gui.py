import os
import threading
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# --- Constants ---
SIDEBAR_WIDTH = 200
DETAIL_WIDTH = 300
COVER_SIZE = (150, 200)
LARGE_COVER_SIZE = (250, 350)
HIGHLIGHT_COLOR = '#1464f4'
THEME = 'superhero'
UI_STATE_FILE = 'ROMForge/ui_state.json'

# --- Helper Functions ---
def load_ui_state():
    if os.path.exists(UI_STATE_FILE):
        with open(UI_STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_ui_state(state):
    os.makedirs(os.path.dirname(UI_STATE_FILE), exist_ok=True)
    with open(UI_STATE_FILE, 'w') as f:
        json.dump(state, f)

def async_load(func):
    def wrapper(*args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper

# --- Main Application ---
class ROMManagerApp(tb.Window):
    def __init__(self):
        super().__init__(themename=THEME)
        self.title('ROMForge Manager')
        self.geometry('1400x900')
        self.minsize(1100, 700)
        self.protocol('WM_DELETE_WINDOW', self.on_exit)
        self.ui_state = load_ui_state()
        self.games = []  # List of game dicts
        self.filtered_games = []
        self.favorites = set(self.ui_state.get('favorites', []))
        self.selected_game = None
        self.cover_cache = {}
        self._build_layout()
        self._load_games_async()

    def _build_layout(self):
        # Top toolbar
        self.toolbar = tb.Frame(self, bootstyle=SECONDARY)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self._build_toolbar()
        # Main layout
        self.main_frame = tb.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        # Sidebar
        self.sidebar = tb.Frame(self.main_frame, width=SIDEBAR_WIDTH, bootstyle=DARK)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        self._build_sidebar()
        # Game grid
        self.grid_frame = tb.Frame(self.main_frame)
        self.grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._build_game_grid()
        # Detail panel
        self.detail_panel = tb.Frame(self.main_frame, width=DETAIL_WIDTH, bootstyle=DARK)
        self.detail_panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.detail_panel.pack_propagate(False)
        self._build_detail_panel()
        # Status bar
        self.status_bar = tb.Frame(self, bootstyle=SECONDARY)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self._build_status_bar()

    def _build_toolbar(self):
        tb.Button(self.toolbar, text='Scan Folder', command=self.scan_folder).pack(side=tk.LEFT, padx=5, pady=5)
        tb.Button(self.toolbar, text='Organize', command=self.organize).pack(side=tk.LEFT, padx=5)
        tb.Button(self.toolbar, text='Settings', command=self.settings).pack(side=tk.LEFT, padx=5)
        tb.Button(self.toolbar, text='Help', command=self.help).pack(side=tk.LEFT, padx=5)
        self.toolbar_search = tb.Entry(self.toolbar, width=30)
        self.toolbar_search.pack(side=tk.RIGHT, padx=10)
        self.toolbar_search.bind('<Return>', lambda e: self.filter_games())
        self.toolbar_search.bind('<Control-f>', lambda e: self.toolbar_search.focus_set())
        # Filters (system, genre, verification)
        self.filter_system = tb.Combobox(self.toolbar, values=['All Systems'], width=12, state='readonly')
        self.filter_system.set('All Systems')
        self.filter_system.pack(side=tk.RIGHT, padx=5)
        self.filter_genre = tb.Combobox(self.toolbar, values=['All Genres'], width=12, state='readonly')
        self.filter_genre.set('All Genres')
        self.filter_genre.pack(side=tk.RIGHT, padx=5)
        self.filter_status = tb.Combobox(self.toolbar, values=['All Status'], width=12, state='readonly')
        self.filter_status.set('All Status')
        self.filter_status.pack(side=tk.RIGHT, padx=5)

    def _build_sidebar(self):
        # Search bar
        search = tb.Entry(self.sidebar, width=18)
        search.pack(padx=10, pady=10)
        search.bind('<Return>', lambda e: self.filter_games())
        # Collapsible categories
        self.sidebar_tree = ttk.Treeview(self.sidebar, show='tree', selectmode='browse', height=30)
        self.sidebar_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # Example categories
        consoles = self.sidebar_tree.insert('', 'end', text='Consoles', open=True)
        handhelds = self.sidebar_tree.insert('', 'end', text='Handhelds', open=True)
        pc = self.sidebar_tree.insert('', 'end', text='PC', open=True)
        # Example systems
        self.sidebar_tree.insert(consoles, 'end', text='SNES', image=self._get_icon('snes.png'))
        self.sidebar_tree.insert(handhelds, 'end', text='Game Boy Advance', image=self._get_icon('gba.png'))
        self.sidebar_tree.insert(pc, 'end', text='DOS', image=self._get_icon('pc.png'))
        self.sidebar_tree.bind('<<TreeviewSelect>>', lambda e: self.filter_games())
        # Favorites toggle
        fav_btn = tb.Button(self.sidebar, text='★ Favorites', command=self.toggle_favorites, bootstyle=INFO)
        fav_btn.pack(pady=5)

    def _get_icon(self, filename):
        # Placeholder: returns a blank image for now
        img = Image.new('RGBA', (32, 32), (20, 30, 40, 255))
        return ImageTk.PhotoImage(img)

    def _build_game_grid(self):
        self.canvas = tk.Canvas(self.grid_frame, bg='#181c22', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Configure>', lambda e: self._draw_game_grid())
        self.canvas.bind('<Double-Button-1>', self._on_game_double_click)
        self.canvas.bind('<Button-3>', self._on_game_right_click)

    def _draw_game_grid(self):
        # Placeholder: draws a grid of rectangles for games
        self.canvas.delete('all')
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        cols = max(1, w // (COVER_SIZE[0] + 30))
        for i in range(12):
            row, col = divmod(i, cols)
            x = 30 + col * (COVER_SIZE[0] + 30)
            y = 30 + row * (COVER_SIZE[1] + 40)
            self.canvas.create_rectangle(x, y, x+COVER_SIZE[0], y+COVER_SIZE[1], outline=HIGHLIGHT_COLOR, width=2)
            self.canvas.create_text(x+COVER_SIZE[0]//2, y+COVER_SIZE[1]+15, text=f"Game {i+1}", fill='white', font=('Segoe UI', 12))

    def _on_game_double_click(self, event):
        # Placeholder: Launch game
        messagebox.showinfo('Launch', 'Launching game...')

    def _on_game_right_click(self, event):
        # Placeholder: Context menu
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label='Validate ROM')
        menu.add_command(label='Download Cover')
        menu.add_command(label='Open File Location')
        menu.add_command(label='Add to Favorites')
        menu.tk_popup(event.x_root, event.y_root)

    def _build_detail_panel(self):
        # Large cover art
        cover = tb.Label(self.detail_panel, text='[Cover]', width=30, bootstyle=SECONDARY)
        cover.pack(pady=20)
        # Metadata
        meta = tb.Label(self.detail_panel, text='Title\nSystem + Year\nDeveloper/Publisher\nGenre/Tags\nFile Info', justify=tk.LEFT, font=('Segoe UI', 12), bootstyle=LIGHT)
        meta.pack(pady=10)
        # Progress bar
        self.progress = tb.Progressbar(self.detail_panel, length=200, bootstyle=INFO)
        self.progress.pack(pady=10)
        # Buttons
        btn_frame = tb.Frame(self.detail_panel)
        btn_frame.pack(pady=10)
        tb.Button(btn_frame, text='Launch in Emulator').pack(side=tk.LEFT, padx=5)
        tb.Button(btn_frame, text='Edit Metadata').pack(side=tk.LEFT, padx=5)

    def _build_status_bar(self):
        stats = tb.Label(self.status_bar, text='42,000 games | 12TB', bootstyle=SECONDARY)
        stats.pack(side=tk.LEFT, padx=10)
        sync = tb.Label(self.status_bar, text='DB: Synced', bootstyle=SUCCESS)
        sync.pack(side=tk.RIGHT, padx=10)
        self.status_progress = tb.Progressbar(self.status_bar, length=200, bootstyle=INFO)
        self.status_progress.pack(side=tk.RIGHT, padx=10)

    @async_load
    def _load_games_async(self):
        # Placeholder: Simulate loading
        import time
        time.sleep(1)
        # Would load games and covers here
        self._draw_game_grid()

    def filter_games(self):
        # Placeholder: Would filter games based on search/filters
        self._draw_game_grid()

    def scan_folder(self):
        messagebox.showinfo('Scan', 'Scan folder feature coming soon!')

    def organize(self):
        messagebox.showinfo('Organize', 'Organize feature coming soon!')

    def settings(self):
        messagebox.showinfo('Settings', 'Settings feature coming soon!')

    def help(self):
        messagebox.showinfo('Help', 'Help feature coming soon!')

    def toggle_favorites(self):
        messagebox.showinfo('Favorites', 'Favorites feature coming soon!')

    def on_exit(self):
        # Save UI state
        self.ui_state['favorites'] = list(self.favorites)
        save_ui_state(self.ui_state)
        self.destroy()

if __name__ == '__main__':
    app = ROMManagerApp()
    app.mainloop()
