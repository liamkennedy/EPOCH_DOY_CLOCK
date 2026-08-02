
import json
import os
import sys
import subprocess
import socket
import tkinter as tk
from tkinter import colorchooser, messagebox
from datetime import datetime, timezone, timedelta
from pathlib import Path

APP_NAME = "Epoch DOY Clock"
SHARED_CONFIG_FILENAME = "epoch_doy_clock.json"
DEVICE_CONFIG_PREFIX = "epoch_doy_clock."

DEFAULT_CONFIG = {
    "window": {
        "x": 100,
        "y": 100,
        "opacity": 0.88,
        "always_on_top": True,
        "remember_position": True
    },
    "appearance": {
        "background": "#2b2723",
        "text_color": "#dddddd",
        "today_color": "#67d46f",
        "future_color": "#e4c84f",
        "past_color": "#e1665f",
        "epoch_font_family": "Segoe UI",
        "epoch_font_size": 24,
        "clock_font_family": "Segoe UI",
        "clock_font_size": 15,
        "date_font_size": 10,
        "offset_font_size": 24,
        "padding_x": 14,
        "padding_y": 8,
        "center_width": 210
    },
    "display": {
        "layout": "horizontal",
        "epoch_format": "GMT {doy:03d}",
        "clock_format": "%H:%M:%S UTC",
        "date_format": "%A %d/%m/%Y",
        "show_seconds": True,
        "offset_zero_text": "0"
    },
    "controls": {
        "mouse_wheel_days": 1,
        "shift_arrow_days": 7,
        "copy_on_epoch_click": True
    }
}


def deep_merge(base, override):
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def app_directory():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


class EpochClockApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.overrideredirect(True)

        self.shared_config_path = app_directory() / SHARED_CONFIG_FILENAME
        self.device_name = self.safe_device_name()
        self.device_config_path = app_directory() / f"{DEVICE_CONFIG_PREFIX}{self.device_name}.json"
        self.config_path = self.device_config_path
        self.config = self.load_config()
        self.offset_days = 0
        self.drag_origin = None
        self.copy_flash_job = None

        self.apply_window_settings()
        self.build_ui()
        self.bind_controls()
        self.build_context_menu()
        self.restore_position()

        self.update_clock()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def safe_device_name(self):
        name = os.environ.get("COMPUTERNAME") or socket.gethostname() or "device"
        safe = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in name.strip())
        return safe or "device"

    def load_json_file(self, path):
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception:
            backup = path.with_suffix(path.suffix + ".invalid")
            try:
                path.replace(backup)
            except Exception:
                pass
            return {}

    def load_config(self):
        shared = self.load_json_file(self.shared_config_path)
        device = self.load_json_file(self.device_config_path)

        config = deep_merge(DEFAULT_CONFIG, shared)
        config = deep_merge(config, device)

        if not self.shared_config_path.exists():
            self.save_shared_config(DEFAULT_CONFIG)

        if not self.device_config_path.exists():
            self.save_config(config)

        return config

    def save_shared_config(self, config):
        try:
            with self.shared_config_path.open("w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass

    def save_config(self, config=None):
        cfg = config if config is not None else self.config
        try:
            with self.device_config_path.open("w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass

    def apply_window_settings(self):
        window_cfg = self.config["window"]
        bg = self.config["appearance"]["background"]
        self.root.configure(bg=bg)
        self.root.attributes("-topmost", bool(window_cfg["always_on_top"]))
        opacity = max(0.25, min(1.0, float(window_cfg["opacity"])))
        self.root.attributes("-alpha", opacity)

    def build_ui(self):
        for child in self.root.winfo_children():
            child.destroy()

        a = self.config["appearance"]
        d = self.config["display"]
        bg = a["background"]
        fg = a["text_color"]
        px = int(a["padding_x"])
        py = int(a["padding_y"])

        self.main = tk.Frame(self.root, bg=bg, padx=px, pady=py)
        self.main.pack(fill="both", expand=True)

        if d["layout"] == "vertical":
            self.build_vertical(bg, fg, a)
        else:
            self.build_horizontal(bg, fg, a)

    def build_horizontal(self, bg, fg, a):
        self.main.grid_columnconfigure(0, weight=0)
        self.main.grid_columnconfigure(1, weight=1, minsize=int(a["center_width"]))
        self.main.grid_columnconfigure(2, weight=0)

        self.epoch_label = tk.Label(
            self.main, text="", bg=bg, fg=fg,
            font=(a["epoch_font_family"], int(a["epoch_font_size"]), "bold"),
            padx=6
        )
        self.epoch_label.grid(row=0, column=0, rowspan=2, sticky="nsew")

        center = tk.Frame(self.main, bg=bg, width=int(a["center_width"]))
        center.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10)
        center.grid_propagate(False)
        center.grid_rowconfigure(0, weight=1)
        center.grid_rowconfigure(1, weight=1)
        center.grid_columnconfigure(0, weight=1)

        self.clock_label = tk.Label(
            center, text="", bg=bg, fg=fg,
            font=(a["clock_font_family"], int(a["clock_font_size"]), "bold"),
            anchor="center", justify="center"
        )
        self.clock_label.grid(row=0, column=0, sticky="nsew")

        self.date_label = tk.Label(
            center, text="", bg=bg, fg=fg,
            font=(a["clock_font_family"], int(a["date_font_size"])),
            anchor="center", justify="center"
        )
        self.date_label.grid(row=1, column=0, sticky="nsew")

        self.offset_label = tk.Label(
            self.main, text="", bg=bg, fg=fg,
            font=(a["epoch_font_family"], int(a["offset_font_size"]), "bold"),
            padx=6
        )
        self.offset_label.grid(row=0, column=2, rowspan=2, sticky="nsew")

    def build_vertical(self, bg, fg, a):
        self.main.grid_columnconfigure(0, weight=1)

        self.epoch_label = tk.Label(
            self.main, text="", bg=bg, fg=fg,
            font=(a["epoch_font_family"], int(a["epoch_font_size"]), "bold"),
            anchor="center", justify="center"
        )
        self.epoch_label.grid(row=0, column=0, sticky="ew")

        self.clock_label = tk.Label(
            self.main, text="", bg=bg, fg=fg,
            font=(a["clock_font_family"], int(a["clock_font_size"]), "bold"),
            anchor="center", justify="center"
        )
        self.clock_label.grid(row=1, column=0, sticky="ew")

        self.date_label = tk.Label(
            self.main, text="", bg=bg, fg=fg,
            font=(a["clock_font_family"], int(a["date_font_size"])),
            anchor="center", justify="center"
        )
        self.date_label.grid(row=2, column=0, sticky="ew")

        self.offset_label = tk.Label(
            self.main, text="", bg=bg, fg=fg,
            font=(a["epoch_font_family"], int(a["offset_font_size"]), "bold"),
            anchor="center", justify="center"
        )
        self.offset_label.grid(row=3, column=0, sticky="ew")

    def bind_controls(self):
        widgets = [self.root] + list(self.walk_widgets(self.root))
        for widget in widgets:
            widget.bind("<ButtonPress-1>", self.start_drag, add="+")
            widget.bind("<B1-Motion>", self.drag, add="+")
            widget.bind("<ButtonRelease-1>", self.end_drag, add="+")
            widget.bind("<Button-3>", self.show_context_menu, add="+")
            widget.bind("<MouseWheel>", self.on_mouse_wheel, add="+")
            widget.bind("<Button-4>", lambda e: self.change_offset(-1), add="+")
            widget.bind("<Button-5>", lambda e: self.change_offset(1), add="+")
            widget.bind("<Enter>", lambda e: self.root.focus_force(), add="+")

        self.root.bind("<Left>", lambda e: self.change_offset(-self.arrow_step(e)))
        self.root.bind("<Right>", lambda e: self.change_offset(self.arrow_step(e)))
        self.root.bind("0", lambda e: self.go_now())
        self.root.bind("<Escape>", lambda e: self.go_now())
        self.root.bind("<Control-c>", lambda e: self.copy_epoch())
        self.root.bind("<Control-q>", lambda e: self.close())
        self.root.bind("<Alt-F4>", lambda e: self.close())
        self.root.bind_all("<Button-3>", self.show_context_menu, add="+")
        self.epoch_label.bind("<ButtonRelease-1>", self.on_epoch_click, add="+")

    def walk_widgets(self, widget):
        for child in widget.winfo_children():
            yield child
            yield from self.walk_widgets(child)

    def arrow_step(self, event):
        shift = bool(event.state & 0x0001)
        return int(self.config["controls"]["shift_arrow_days"]) if shift else 1

    def start_drag(self, event):
        self.drag_origin = (event.x_root, event.y_root, self.root.winfo_x(), self.root.winfo_y())
        self.root.focus_force()

    def drag(self, event):
        if not self.drag_origin:
            return
        sx, sy, wx, wy = self.drag_origin
        self.root.geometry(f"+{wx + event.x_root - sx}+{wy + event.y_root - sy}")

    def end_drag(self, event):
        self.drag_origin = None
        self.save_position()

    def on_mouse_wheel(self, event):
        step = int(self.config["controls"]["mouse_wheel_days"])
        self.change_offset(-step if event.delta > 0 else step)

    def on_epoch_click(self, event):
        if self.config["controls"].get("copy_on_epoch_click", True):
            self.copy_epoch()

    def update_clock(self):
        now = datetime.now(timezone.utc)
        selected = now + timedelta(days=self.offset_days)

        doy = selected.timetuple().tm_yday
        fmt = self.config["display"]["epoch_format"]
        try:
            epoch_text = fmt.format(
                year=selected.year,
                doy=doy,
                hour=selected.hour,
                minute=selected.minute,
                second=selected.second
            )
        except Exception:
            epoch_text = f"GMT {doy:03d}"

        clock_format = self.config["display"]["clock_format"]
        if not self.config["display"].get("show_seconds", True):
            clock_format = clock_format.replace(":%S", "")

        self.epoch_label.config(text=epoch_text)
        self.clock_label.config(text=selected.strftime(clock_format))
        self.date_label.config(text=selected.strftime(self.config["display"]["date_format"]))

        zero_text = str(self.config["display"].get("offset_zero_text", "0"))
        offset_text = zero_text if self.offset_days == 0 else f"{self.offset_days:+d}"
        self.offset_label.config(text=offset_text)

        color = self.current_status_color()
        self.epoch_label.config(fg=color)
        self.offset_label.config(fg=color)

        delay = 200 if self.config["display"].get("show_seconds", True) else 1000
        self.root.after(delay, self.update_clock)

    def current_status_color(self):
        a = self.config["appearance"]
        if self.offset_days == 0:
            return a["today_color"]
        if self.offset_days > 0:
            return a["future_color"]
        return a["past_color"]

    def change_offset(self, amount):
        self.offset_days += int(amount)
        self.root.focus_force()

    def go_now(self):
        self.offset_days = 0
        self.root.focus_force()

    def copy_epoch(self):
        now = datetime.now(timezone.utc) + timedelta(days=self.offset_days)
        doy = now.timetuple().tm_yday
        try:
            text = self.config["display"]["epoch_format"].format(
                year=now.year, doy=doy,
                hour=now.hour, minute=now.minute, second=now.second
            )
        except Exception:
            text = f"GMT {doy:03d}"
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.flash_copy_feedback()

    def copy_full_timestamp(self):
        selected = datetime.now(timezone.utc) + timedelta(days=self.offset_days)
        doy = selected.timetuple().tm_yday
        text = f"GMT {doy:03d}/{selected:%H:%M:%S} ({selected:%A %d/%m/%Y})"
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.flash_copy_feedback()

    def flash_copy_feedback(self):
        original = self.date_label.cget("text")
        self.date_label.config(text="Copied")
        if self.copy_flash_job:
            try:
                self.root.after_cancel(self.copy_flash_job)
            except Exception:
                pass
        self.copy_flash_job = self.root.after(650, lambda: self.date_label.config(text=original))

    def build_context_menu(self):
        self.menu = tk.Menu(self.root, tearoff=False)
        self.menu.add_command(label="Now", command=self.go_now)
        self.menu.add_separator()
        self.menu.add_command(label="Copy Epoch", command=self.copy_epoch)
        self.menu.add_command(label="Copy Full Timestamp", command=self.copy_full_timestamp)
        self.menu.add_separator()

        layout_menu = tk.Menu(self.menu, tearoff=False)
        layout_menu.add_command(label="Horizontal", command=lambda: self.set_layout("horizontal"))
        layout_menu.add_command(label="Vertical", command=lambda: self.set_layout("vertical"))
        self.menu.add_cascade(label="Layout", menu=layout_menu)

        opacity_menu = tk.Menu(self.menu, tearoff=False)
        for percent in (100, 90, 80, 70, 60, 50):
            opacity_menu.add_command(
                label=f"{percent}%",
                command=lambda p=percent: self.set_opacity(p / 100.0)
            )
        self.menu.add_cascade(label="Opacity", menu=opacity_menu)

        self.topmost_var = tk.BooleanVar(value=bool(self.config["window"]["always_on_top"]))
        self.menu.add_checkbutton(
            label="Always on Top",
            variable=self.topmost_var,
            command=self.toggle_topmost
        )
        self.menu.add_command(label="Edit This Device Settings", command=self.open_settings_file)
        self.menu.add_command(label="Edit Shared Defaults", command=self.open_shared_settings_file)
        self.menu.add_command(label="Reload Settings", command=self.reload_settings)
        self.menu.add_command(label="Restore Defaults", command=self.restore_defaults)
        self.menu.add_separator()
        self.menu.add_command(label="Help", command=self.show_help)
        self.menu.add_separator()
        self.menu.add_command(label="Close", command=self.close)

    def show_context_menu(self, event):
        self.root.focus_force()
        try:
            self.menu.unpost()
        except Exception:
            pass

        # Use post() rather than tk_popup(). tk_popup() creates a temporary
        # grab which can become stuck when the layout is rebuilt from a menu
        # command on some Windows/Tk versions.
        self.menu.post(event.x_root, event.y_root)
        return "break"

    def show_help(self):
        try:
            self.menu.unpost()
        except Exception:
            pass

        help_window = tk.Toplevel(self.root)
        help_window.overrideredirect(True)
        help_window.attributes("-topmost", True)

        a = self.config["appearance"]
        bg = a["background"]
        fg = a["text_color"]
        accent = self.current_status_color()

        outer = tk.Frame(
            help_window,
            bg=accent,
            padx=1,
            pady=1
        )
        outer.pack(fill="both", expand=True)

        panel = tk.Frame(
            outer,
            bg=bg,
            padx=18,
            pady=14
        )
        panel.pack(fill="both", expand=True)

        title = tk.Label(
            panel,
            text="EPOCH DOY CLOCK — CONTROLS",
            bg=bg,
            fg=accent,
            font=(a["clock_font_family"], 12, "bold")
        )
        title.pack(pady=(0, 10))

        controls = [
            ("Left Arrow", "Previous day"),
            ("Right Arrow", "Next day"),
            ("Shift + Arrow", "Move 7 days"),
            ("0 or Escape", "Return to UTC now"),
            ("Mouse Wheel", "Move backward / forward one day"),
            ("Ctrl + C", "Copy displayed Epoch DOY"),
            ("Click Epoch", "Copy displayed Epoch DOY"),
            ("Left-drag", "Move the widget"),
            ("Right-click", "Open menu"),
            ("Ctrl + Q / Alt + F4", "Close the widget"),
        ]

        grid = tk.Frame(panel, bg=bg)
        grid.pack()

        for row, (key, action) in enumerate(controls):
            tk.Label(
                grid,
                text=key,
                bg=bg,
                fg=fg,
                font=(a["clock_font_family"], 10, "bold"),
                anchor="e",
                justify="right",
                padx=6,
                pady=2
            ).grid(row=row, column=0, sticky="e")

            tk.Label(
                grid,
                text=action,
                bg=bg,
                fg=fg,
                font=(a["clock_font_family"], 10),
                anchor="w",
                justify="left",
                padx=6,
                pady=2
            ).grid(row=row, column=1, sticky="w")

        footer = tk.Label(
            panel,
            text="Click anywhere or press Enter / Space / Escape to close",
            bg=bg,
            fg=fg,
            font=(a["clock_font_family"], 9),
            pady=10
        )
        footer.pack()

        help_window.update_idletasks()

        # Center the help overlay over the main widget.
        x = self.root.winfo_x() + max(
            0, (self.root.winfo_width() - help_window.winfo_width()) // 2
        )
        y = self.root.winfo_y() + max(
            0, (self.root.winfo_height() - help_window.winfo_height()) // 2
        )
        help_window.geometry(f"+{x}+{y}")

        def close_help(event=None):
            try:
                help_window.destroy()
            except Exception:
                pass
            self.root.focus_force()
            return "break"

        for widget in [help_window] + list(self.walk_widgets(help_window)):
            widget.bind("<Button-1>", close_help, add="+")

        help_window.bind("<Escape>", close_help)
        help_window.bind("<Return>", close_help)
        help_window.bind("<space>", close_help)
        help_window.bind("<Control-q>", close_help)
        help_window.focus_force()

    def set_layout(self, layout):
        if self.config["display"].get("layout") == layout:
            try:
                self.menu.unpost()
            except Exception:
                pass
            return

        self.config["display"]["layout"] = layout
        self.save_position()
        self.save_config()

        try:
            self.menu.unpost()
        except Exception:
            pass

        # Restarting avoids a Windows/Tkinter issue where rebuilding a
        # borderless window from a menu command can break later right-clicks.
        self.root.after(100, self.restart_app)

    def restart_app(self):
        try:
            if getattr(sys, "frozen", False):
                command = [sys.executable]
                working_dir = str(Path(sys.executable).resolve().parent)
            else:
                command = [sys.executable, str(Path(__file__).resolve())]
                working_dir = str(Path(__file__).resolve().parent)

            # Launch the replacement process first, then close this instance.
            # This is more reliable on Windows than replacing a pythonw.exe
            # process with os.execl().
            subprocess.Popen(
                command,
                cwd=working_dir,
                close_fds=True
            )
        except Exception as exc:
            messagebox.showerror(
                APP_NAME,
                f"Could not restart the widget automatically:\n{exc}\n\n"
                "The new layout has been saved. Please start the widget again."
            )
        finally:
            self.root.destroy()

    def set_opacity(self, opacity):
        self.config["window"]["opacity"] = opacity
        self.root.attributes("-alpha", opacity)
        self.save_config()

    def toggle_topmost(self):
        value = bool(self.topmost_var.get())
        self.config["window"]["always_on_top"] = value
        self.root.attributes("-topmost", value)
        self.save_config()

    def open_settings_file(self):
        self.save_config()
        try:
            os.startfile(self.config_path)
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Could not open settings file:\n{exc}")

    def open_shared_settings_file(self):
        if not self.shared_config_path.exists():
            self.save_shared_config(DEFAULT_CONFIG)
        try:
            os.startfile(self.shared_config_path)
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Could not open shared settings file:\n{exc}")

    def reload_settings(self):
        current_x, current_y = self.root.winfo_x(), self.root.winfo_y()
        self.config = self.load_config()
        self.apply_window_settings()
        self.build_ui()
        self.bind_controls()
        self.root.geometry(f"+{current_x}+{current_y}")
        self.build_context_menu()

    def restore_defaults(self):
        if not messagebox.askyesno(APP_NAME, "Restore all default settings?"):
            return
        current_x, current_y = self.root.winfo_x(), self.root.winfo_y()
        shared = self.load_json_file(self.shared_config_path)
        self.config = deep_merge(DEFAULT_CONFIG, shared)
        self.config["window"]["x"] = current_x
        self.config["window"]["y"] = current_y
        self.save_config()
        self.apply_window_settings()
        self.build_ui()
        self.bind_controls()
        self.build_context_menu()

    def restore_position(self):
        self.root.update_idletasks()

        x = int(self.config["window"].get("x", 100))
        y = int(self.config["window"].get("y", 100))

        widget_w = max(1, self.root.winfo_reqwidth())
        widget_h = max(1, self.root.winfo_reqheight())
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        visible_margin = 40
        off_screen = (
            x > screen_w - visible_margin or
            y > screen_h - visible_margin or
            x + widget_w < visible_margin or
            y + widget_h < visible_margin
        )

        if off_screen:
            x, y = 100, 100
            self.config["window"]["x"] = x
            self.config["window"]["y"] = y
            self.save_config()

        self.root.geometry(f"+{x}+{y}")

    def save_position(self):
        if not self.config["window"].get("remember_position", True):
            return
        self.config["window"]["x"] = self.root.winfo_x()
        self.config["window"]["y"] = self.root.winfo_y()
        self.save_config()

    def close(self):
        self.save_position()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    EpochClockApp().run()
