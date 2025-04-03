import os
import sys
import subprocess

def build_app():
    """Build the Minecraft Backup App into a standalone executable"""
    print("🔧 Building Minecraft Backup App...")

    # Archivos adicionales: incluir toda la carpeta resources
    data_option = "--add-data=resources:resources"
    if sys.platform == "win32":
        icon_option = "--icon=resources/appgenius_icon.ico"
    elif sys.platform == "darwin":
        icon_option = "--icon=resources/app_icon.icns"
    else:
        icon_option = ""

    # Comando base para PyInstaller
    cmd = [
        "pyinstaller",
        "--name=MinecraftBackupTool",
        "--onefile",
        "--windowed",
        icon_option,
        data_option,
        "main.py"
    ]

    # Config extra para macOS
    if sys.platform == "darwin":
        cmd.append("--osx-bundle-identifier=com.minecraftbackuptool")

    try:
        subprocess.check_call(cmd)
        print("\n✅ Build successful!")

        if sys.platform == "win32":
            print(f"🪟 Executable created at: dist/MinecraftBackupTool.exe")
        elif sys.platform == "darwin":
            print(f"🍎 App created at: dist/MinecraftBackupTool.app")
        else:
            print("🛠️ Executable created in dist/")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error: {e}")
        return False

    return True

if __name__ == "__main__":
    build_app()
