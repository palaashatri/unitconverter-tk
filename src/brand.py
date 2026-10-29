"""Brand identity assets, color palette, and platform icon integration."""

from pathlib import Path
import sys
import tkinter as tk
from typing import Optional


# Brand Color Palette based on assets/brand/palette.json
BRAND_ACCENT = "#23C9D4"       # Vibrant Turquoise / Cyan from conversion arrow
BRAND_ACCENT_HOVER = "#1BA8B2" # Darker turquoise for hover
BRAND_ACCENT_ACTIVE = "#158B94"# Deep turquoise
BRAND_GOLD = "#F59E0B"         # Warm Gold / Amber from crossing arrow
BRAND_GOLD_HOVER = "#D97706"

# Dark Theme (matching #101720 obsidian background from palette.json)
DARK_BG = "#101720"
DARK_SURFACE = "#17212E"
DARK_CARD = "#1C2737"
DARK_INPUT = "#0D131C"
DARK_BORDER = "#27364B"
DARK_BORDER_FOCUS = "#23C9D4"
DARK_TEXT = "#F4F7FC"
DARK_TEXT_MUTED = "#94A3B8"
DARK_TEXT_HINT = "#64748B"

# Light Theme
LIGHT_BG = "#F8FAFC"
LIGHT_SURFACE = "#FFFFFF"
LIGHT_CARD = "#FFFFFF"
LIGHT_INPUT = "#F1F5F9"
LIGHT_BORDER = "#E2E8F0"
LIGHT_BORDER_FOCUS = "#0EA5E9"
LIGHT_TEXT = "#0F172A"
LIGHT_TEXT_MUTED = "#475569"
LIGHT_TEXT_HINT = "#94A3B8"

# Status colors
COLOR_SUCCESS = "#10B981"
COLOR_ERROR = "#EF4444"
COLOR_INFO = BRAND_ACCENT

def get_brand_photo(size: int = 64, master: Optional[tk.Widget] = None) -> Optional[tk.PhotoImage]:
    """Load a brand PNG icon as a PhotoImage bound to master."""
    if master is not None:
        root = master.winfo_toplevel() if hasattr(master, "winfo_toplevel") else master
        cache = getattr(root, "_brand_photos", None)
        if cache is None:
            cache = {}
            root._brand_photos = cache
        key = f"icon_{size}"
        if key in cache:
            return cache[key]
    else:
        root = None
        key = f"icon_{size}"

    target_files = [
        f"icon-{size}.png",
        f"icon-64.png",
        f"icon-32.png",
        f"icon-128.png",
        "icon-source-crop.png",
    ]

    for candidate in target_files:
        path = get_brand_asset_path(candidate)
        if path and path.is_file():
            try:
                photo = tk.PhotoImage(file=str(path), master=root)
                if root is not None:
                    root._brand_photos[key] = photo
                return photo
            except Exception:
                continue

    return None


def get_asset_dir() -> Path:
    """Locate the brand assets directory across development and frozen environments."""
    # PyInstaller temporary bundle directory
    if hasattr(sys, "_MEIPASS"):
        candidate = Path(sys._MEIPASS) / "assets" / "brand"
        if candidate.is_dir():
            return candidate

    # macOS app bundle Resources directory
    executable_dir = Path(sys.executable).resolve().parent
    if executable_dir.name == "MacOS":
        candidate = executable_dir.parent / "Resources" / "assets" / "brand"
        if candidate.is_dir():
            return candidate

    # Source tree root relative to this module
    repo_root = Path(__file__).resolve().parent.parent
    candidate = repo_root / "assets" / "brand"
    if candidate.is_dir():
        return candidate

    # Fallback to local assets
    return repo_root / "assets"


def get_brand_asset_path(filename: str) -> Optional[Path]:
    """Return the absolute path to a brand asset file if it exists."""
    asset_dir = get_asset_dir()
    path = asset_dir / filename
    if path.is_file():
        return path
    # Try directly under assets/
    parent_path = asset_dir.parent / filename
    if parent_path.is_file():
        return parent_path
    return None


def set_macos_dock_icon() -> bool:
    """Set the application icon in the macOS Dock dynamically via Cocoa AppKit."""
    if sys.platform != "darwin":
        return False

    icon_path = get_brand_asset_path("icon-512.png")
    if not icon_path or not icon_path.is_file():
        icon_path = get_brand_asset_path("icon-256.png")
    if not icon_path or not icon_path.is_file():
        icon_path = get_brand_asset_path("icon-source-crop.png")
    if not icon_path or not icon_path.is_file():
        return False

    try:
        import ctypes

        ctypes.cdll.LoadLibrary("/System/Library/Frameworks/AppKit.framework/AppKit")
        objc = ctypes.cdll.LoadLibrary("/usr/lib/libobjc.A.dylib")

        objc.objc_getClass.restype = ctypes.c_void_p
        objc.objc_getClass.argtypes = [ctypes.c_char_p]

        objc.sel_registerName.restype = ctypes.c_void_p
        objc.sel_registerName.argtypes = [ctypes.c_char_p]

        def msg_send(target, sel_name, *args, argtypes=None):
            sel = objc.sel_registerName(sel_name.encode("utf-8"))
            func = objc.objc_msgSend
            func.restype = ctypes.c_void_p
            if argtypes is None:
                argtypes = [ctypes.c_void_p, ctypes.c_void_p] + [ctypes.c_void_p] * len(args)
            func.argtypes = argtypes
            return func(target, sel, *args)

        ns_app_cls = objc.objc_getClass(b"NSApplication")
        app = msg_send(ns_app_cls, "sharedApplication")

        ns_string_cls = objc.objc_getClass(b"NSString")
        abs_path = str(icon_path.resolve()).encode("utf-8")
        path_str = msg_send(
            ns_string_cls,
            "stringWithUTF8String:",
            abs_path,
            argtypes=[ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p],
        )

        ns_image_cls = objc.objc_getClass(b"NSImage")
        img_alloc = msg_send(ns_image_cls, "alloc")
        img = msg_send(img_alloc, "initWithContentsOfFile:", path_str)

        if img:
            msg_send(app, "setApplicationIconImage:", img)
            return True
    except Exception:
        pass
    return False


def apply_app_icon(root: tk.Tk) -> None:
    """Apply the brand icon across all supported platforms (macOS, Windows, Linux)."""
    # 1. On macOS, update the dock icon dynamically
    if sys.platform == "darwin":
        set_macos_dock_icon()

    # 2. On Windows, set window and taskbar icon using the native ICO
    if sys.platform.startswith("win"):
        ico_path = get_brand_asset_path("icon.ico")
        if ico_path and ico_path.is_file():
            try:
                root.iconbitmap(str(ico_path))
            except Exception:
                pass

    # 3. Cross-platform Tk iconphoto (Linux, Windows, and X11/Tk window decorations)
    photo = get_brand_photo(64, master=root) or get_brand_photo(32, master=root)
    if photo:
        try:
            root.iconphoto(True, photo)
            # Store reference on root to keep it alive
            root._app_icon_photo = photo
        except Exception:
            pass


def detect_system_dark_mode() -> bool:
    """Detect whether system dark mode is active."""
    platform = sys.platform
    try:
        if platform == "darwin":
            import subprocess

            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                timeout=1,
            )
            return "Dark" in result.stdout
        elif platform.startswith("win"):
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
    except Exception:
        pass
    return False
