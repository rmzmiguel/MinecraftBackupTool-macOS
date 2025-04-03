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
        cmd.extend([
            "--osx-bundle-identifier=com.minecraftbackuptool",
            "--target-arch=universal2",  # Binario universal para Intel y ARM
            "--hidden-import=tkinter",  # Asegura que tkinter se empaquete correctamente
        ])

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("\n✅ Build successful!")
        print(f"PyInstaller stdout: {result.stdout}")
        print(f"PyInstaller stderr: {result.stderr}")

        if sys.platform == "win32":
            print(f"🪟 Executable created at: dist/MinecraftBackupTool.exe")
        elif sys.platform == "darwin":
            print(f"🍎 App created at: dist/MinecraftBackupTool.app")
            # Mostrar la estructura del bundle para depuración
            print("📂 Bundle structure:")
            subprocess.run(["ls", "-R", "dist/MinecraftBackupTool.app"])
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
