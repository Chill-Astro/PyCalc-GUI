import os
import sys
import shutil
import subprocess

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)

def detect_os_theme():
    # Returns 'dark' or 'light'. Enhanced for KDE (KWin) and GNOME on Wayland.
    try:
        if sys.platform == 'win32':
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return 'dark' if value == 0 else 'light'
        elif sys.platform == 'darwin':
            result = subprocess.run([
                'defaults', 'read', '-g', 'AppleInterfaceStyle'
            ], capture_output=True, text=True)
            return 'dark' if 'Dark' in result.stdout else 'light'
        elif sys.platform.startswith('linux'):
            # Wayland only: check XDG_SESSION_TYPE
            if os.environ.get('XDG_SESSION_TYPE', '').lower() == 'wayland':
                desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
                # GNOME Wayland
                if 'gnome' in desktop:
                    try:
                        # GNOME 42+ uses color-scheme, fallback to gtk-theme
                        result = subprocess.run([
                            'gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'
                        ], capture_output=True, text=True)
                        if 'dark' in result.stdout.lower():
                            return 'dark'
                        elif 'light' in result.stdout.lower():
                            return 'light'
                    except Exception:
                        pass
                    # Fallback: check gtk-theme
                    try:
                        result = subprocess.run([
                            'gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'
                        ], capture_output=True, text=True)
                        if 'dark' in result.stdout.lower():
                            return 'dark'
                    except Exception:
                        pass
                # KDE (KWin) Wayland
                elif 'kde' in desktop or 'plasma' in desktop:
                    # KDE Plasma 5.24+ uses color-scheme
                    try:
                        result = subprocess.run([
                            'qdbus', 'org.kde.KWin', '/KWin', 'org.kde.KWin.supportInformation'
                        ], capture_output=True, text=True)
                        # Not strictly needed, but confirms KWin is running
                    except Exception:
                        pass
                    # Try reading kdeglobals config for color scheme
                    kdeglobals_path = os.path.expanduser('~/.config/kdeglobals')
                    if os.path.exists(kdeglobals_path):
                        try:
                            with open(kdeglobals_path, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if line.strip().startswith('ColorScheme='):  # KDE6
                                        scheme = line.strip().split('=', 1)[-1].lower()
                                        if 'dark' in scheme:
                                            return 'dark'
                                        elif 'light' in scheme:
                                            return 'light'
                                    elif line.strip().startswith('name='):  # KDE5
                                        scheme = line.strip().split('=', 1)[-1].lower()
                                        if 'dark' in scheme:
                                            return 'dark'
                                        elif 'light' in scheme:
                                            return 'light'
                        except Exception:
                            pass
                    # Fallback: check KDE_COLOR_SCHEME env
                    kde_scheme = os.environ.get('KDE_COLOR_SCHEME', '').lower()
                    if 'dark' in kde_scheme:
                        return 'dark'
                    elif 'light' in kde_scheme:
                        return 'light'
                # Fallback for other desktops on Wayland
                gtk_theme = os.environ.get('GTK_THEME', '').lower()
                if 'dark' in gtk_theme:
                    return 'dark'
                elif 'light' in gtk_theme:
                    return 'light'
            # Try darkman if available (works for both X11/Wayland)
            if shutil.which('darkman'):
                try:
                    result = subprocess.run(['darkman', 'get'], capture_output=True, text=True)
                    if 'dark' in result.stdout.lower():
                        return 'dark'
                    elif 'light' in result.stdout.lower():
                        return 'light'
                except Exception:
                    pass
            # Fallback: try GTK_THEME or KDE_COLOR_SCHEME
            gtk_theme = os.environ.get('GTK_THEME', '').lower()
            if 'dark' in gtk_theme:
                return 'dark'
            elif 'light' in gtk_theme:
                return 'light'
            kde_scheme = os.environ.get('KDE_COLOR_SCHEME', '').lower()
            if 'dark' in kde_scheme:
                return 'dark'
            elif 'light' in kde_scheme:
                return 'light'
            # Fallback: try XDG_CURRENT_DESKTOP for GNOME/KDE
            desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
            if 'gnome' in desktop or 'kde' in desktop:
                # Try to read gsettings (GNOME)
                try:
                    result = subprocess.run([
                        'gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'
                    ], capture_output=True, text=True)
                    if 'dark' in result.stdout.lower():
                        return 'dark'
                    elif 'light' in result.stdout.lower():
                        return 'light'
                except Exception:
                    pass
            # Default to dark
            return 'dark'
    except Exception:
        return 'dark'
    return 'dark'
