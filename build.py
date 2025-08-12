import os
import sys
import platform
import subprocess
from pathlib import Path
import shutil

# -------- User Configuration --------
MAIN_SCRIPT = "main.py"  # Change if your main script is different
ASSETS_SRC = Path("assets")  # Relative to this script's location
ICON_PATH = ASSETS_SRC / "images" / "logo.ico"  # Path to your icon file for exe
DIST_DIR = Path("dist")
BUILD_DIR = Path("build")
# ------------------------------------


def check_pyinstaller():
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def build_command(current_platform):
    # Set --add-data flag syntax and icon flag
    if os.name == "nt":  # Windows
        add_data = f"{ASSETS_SRC}{os.pathsep}assets"
        icon_flag = ["--icon", str(ICON_PATH)] if ICON_PATH.exists() else []
    else:  # POSIX (Linux/macOS)
        add_data = f"{ASSETS_SRC}:assets"
        # .ico icons are not supported on Linux/macOS for PyInstaller, use .icns for macOS if available
        if current_platform == "darwin" and ICON_PATH.with_suffix(".icns").exists():
            icon_flag = ["--icon", str(ICON_PATH.with_suffix(".icns"))]
        else:
            icon_flag = []

    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--add-data",
        add_data,
        *icon_flag,
        MAIN_SCRIPT,
    ]
    return cmd


def copy_assets_to_dist():
    """
    Ensure the assets folder is present in the dist directory after build.
    """
    dist_assets = DIST_DIR / "assets"
    if dist_assets.exists():
        shutil.rmtree(dist_assets)
    shutil.copytree(ASSETS_SRC, dist_assets)
    print(f"Copied {ASSETS_SRC} to {dist_assets}.")


def clean():
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    for spec in Path(".").glob("*.spec"):
        spec.unlink()
    print("Cleaned previous builds.")


def main():
    print("One-click PyInstaller build script.")
    print("This script must be run on the OS you want to build for.")
    print("---------------------------------------------------------")
    print("1. Clean previous build")
    print("2. Build for current platform")
    print("---------------------------------------------------------")
    clean()
    check_pyinstaller()
    current_platform = platform.system().lower()
    cmd = build_command(current_platform)
    print(f"Running: {' '.join(map(str, cmd))}")
    subprocess.check_call(cmd)
    # Copy assets folder to dist so it is available for the onefile binary
    copy_assets_to_dist()
    if current_platform == "windows":
        print("Your EXE and assets are in the dist/ folder.")
    elif current_platform == "linux":
        print("Your Linux binary and assets are in the dist/ folder.")
    elif current_platform == "darwin":
        print("Your macOS binary and assets are in the dist/ folder.")
    else:
        print(f"Unsupported platform: {current_platform}")
        sys.exit(1)
    print("Done!")


if __name__ == "__main__":
    main()