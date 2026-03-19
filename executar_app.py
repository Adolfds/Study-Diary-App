import subprocess
import os
import sys
import multiprocessing

def get_path(relative_path):
    """ Obtém o caminho absoluto, funciona tanto em dev quanto no executável do PyInstaller """
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    """ A função que inicia o aplicativo Streamlit. """
    app_file = get_path("app.py")
    
    # Monta o comando para rodar o Streamlit
    command = [sys.executable, "-m", "streamlit", "run", app_file, "--server.headless=true"]
    
    # Executa o comando
    subprocess.run(command)


if __name__ == "__main__":

    multiprocessing.freeze_support()
    

    main()