# Design review checklist

The rendered 3D icon **and all 14 binary assets** are integrated into the application: PNG sizes 16–1024px, ICO, ICNS, wordmark, social preview and source crop.

- [x] Export and verify PNG/ICO/ICNS formats
- [x] Check alpha and legibility at 16/24/32px: alpha transparency verified on both dark (#101720) and light backgrounds
- [x] High-resolution asset generation and verification across all sizes
- [x] Integrate approved art into application launcher, installer, and runtime resource paths:
  - macOS: Cocoa AppKit dock icon integration (`src/brand.py`), py2app `iconfile` bundle configuration (`setup-macos.py`)
  - Windows: Window and taskbar icon configuration (`icon.ico`), PyInstaller resource flag
  - Linux: Dynamic window icon loading (`iconphoto`), AppImage desktop icon integration
  - In-app: Polished macOS HIG branded title header and high-resolution About modal dialog
  - Brand Palette: `#23C9D4` (Primary Turquoise), `#F59E0B` (Amber Gold), `#101720` (Obsidian Charcoal), `#F4F7FC` (Foreground Text)

