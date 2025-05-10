import subprocess, os
from datetime import datetime


def hacer_commit():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje = f"Commit automático - sesión cerrada - {timestamp}"

    subprocess.run(["git", "config", "user.name", "SerGioAMM"])
    subprocess.run(["git", "config", "user.email", "sergiomurcia01@gmail.com"])
    subprocess.run(["git", "add", "Data/Biblioteca_GM.db"])
    subprocess.run(["git", "commit", "-m", mensaje])


    # Construir la URL segura con token y usuario desde variables de entorno
    REPO_URL = f"https://{os.environ['GITHUB_USER']}:{os.environ['GITHUB_TOKEN']}@github.com/SerGioAMM/Biblioteca_V3.git"
    #REPO_URL = "https://SerGioAMM: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@github.com/SerGioAMM/Biblioteca_V3.git"


    # Hacer push al repositorio
    subprocess.run(["git", "push", REPO_URL])
