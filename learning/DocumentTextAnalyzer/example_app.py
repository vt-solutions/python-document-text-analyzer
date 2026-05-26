from pathlib import Path
import tkinter as tk

from components.common_ui import (
    Theme,
    create_main_window,
    create_standard_layout,
    VTButton,
    VTDropZone,
    VTTextPanel,
)

BASE_DIR = Path(__file__).resolve().parent
THEME_PATH = BASE_DIR / "design" / "theme.json"

theme = Theme.from_json(THEME_PATH)

root = create_main_window("VT Example App", theme)

header, main, footer = create_standard_layout(
    root,
    theme,
    app_title="VT Example App",
    subtitle="Beispiel-App im einheitlichen Phyton-/VT-Solutions-Design",
    version="1.0.0",
)

VTButton(main, theme, "📂  Datei auswählen", variant="primary", min_width=20).pack(anchor="w", pady=(0, 22))

drop_zone = VTDropZone(main, theme)
drop_zone.pack(fill="x", pady=(0, 16), ipady=6)

text_panel = VTTextPanel(main, theme)
text_panel.pack(fill="both", expand=True, pady=(0, 18))

button_row = tk.Frame(main, bg=theme.colors["app_background"])
button_row.pack(fill="x")

VTButton(button_row, theme, "📋  Alles kopieren", variant="success", min_width=20).pack(side="left", expand=True, padx=(260, 10))
VTButton(button_row, theme, "💾  Text speichern", variant="secondary", min_width=20).pack(side="left", expand=True, padx=10)
VTButton(button_row, theme, "🗑  Text leeren", variant="danger", min_width=20).pack(side="left", expand=True, padx=(10, 0))

root.mainloop()
