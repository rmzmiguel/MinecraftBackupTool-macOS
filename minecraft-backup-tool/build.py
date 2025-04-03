import os
import sys
import subprocess

def build_app():
    """Build the Minecraft Backup App into a standalone executable"""
    print("🔧 Building Minecraft Backup App...")

    # Archivos adicionales: incluir toda la carpeta resources
    data_option = f"--add-data=resources{os.pathsep}resources"

    # Configuración del ícono
    if sys.platform == "win32":
        icon_path = "resources/appgenius_icon.ico"
        if not os.path.exists(icon_path):
            print(f"❌ Error: Icon file {icon_path} not found!")
            sys.exit(1)
        icon_option = f"--icon={icon_path}"
    elif sys.platform == "darwin":
        icon_path = "resources/app_icon.icns"
        if not os.path.exists(icon_path):
            print(f"❌ Error: Icon file {icon_path} not found!")
            sys.exit(1)
        icon_option = f"--icon={icon_path}"
    else:
        icon_option = ""

    # Comando base para PyInstaller
    cmd = [
        "pyinstaller",
        "--name=MinecraftBackupTool",
        "--windowed",  # Modo GUI
        icon_option,
        data_option,
        "main.py"
    ]

    # Config extra para macOS
    if sys.platform == "darwin":
        cmd.append("--osx-bundle-identifier=com.minecraftbackuptool")
        cmd.append("--target-arch=universal2")  # Binario universal para Intel y ARM

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("\n✅ Build successful!")

        if sys.platform == "win32":
            print(f"🪟 Executable created at: dist/MinecraftBackupTool.exe")
        elif sys.platform == "darwin":
            print(f"🍎 App created at: dist/MinecraftBackupTool.app")
        else:
            print("🛠️ Executable created in dist/")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

    return True

if __name__ == "__main__":
    build_app()
