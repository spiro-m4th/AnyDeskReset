import os
import shutil
import subprocess
import time
import logging
import logging.handlers
import sys
import ctypes
import winreg
import requests

# Tenta importar bibliotecas externas, avisa se faltar
try:
    import pyfiglet
    import tkinter as tk
    from tkinter import filedialog
    from colorama import init as colorama_init, Fore, Back, Style
    from tqdm import tqdm
except ImportError as e:
    print(f"Erro crítico: Biblioteca faltando. Instale as dependências: {e}")
    print("Execute: pip install -r requirements.txt")
    input("Pressione Enter para sair...")
    sys.exit(1)

# Importa os módulos locais que acabamos de limpar
try:
    import faq
    from id_changer import change_id
    from backup_restore import (
        backup_user_conf,
        restore_user_conf_interactive,
        set_backup_location_interactive,
        backup_screen_recordings,
        restore_screen_recordings
    )
except ImportError as e:
    print(f"Erro ao importar módulos locais: {e}")
    print("Verifique se id_changer.py, backup_restore.py e faq.py estão na mesma pasta.")
    input("Pressione Enter para sair...")
    sys.exit(1)

# --- Configuração de Log ---
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILENAME = f'anydesk_utils_{timestamp}.log'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Limpa handlers anteriores para evitar duplicidade
for handler in logger.handlers[:]:
    logger.removeHandler(handler)
    handler.close()

try:
    file_handler = logging.FileHandler(LOG_FILENAME, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
except Exception as log_e:
    print(f"Aviso: Não foi possível configurar o log em arquivo {LOG_FILENAME}: {log_e}", file=sys.stderr)

logger.info("=" * 30 + f" Iniciando Script AnyDesk Utils (Log: {LOG_FILENAME}) " + "=" * 30)
logger.info(f"Idioma: Português (PT-BR)")

colorama_init(autoreset=True)  # Inicialização do colorama


# --- Utilitários Básicos ---

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def is_admin():
    """Verifica se o script está rodando como administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def ask_yes_no(question_text):
    """Pergunta Sim/Não ao usuário."""
    while True:
        choice = input(Style.BRIGHT + Fore.LIGHTCYAN_EX + f"{question_text} (s/n): ").strip().lower()
        if choice in ['s', 'y', 'sim']:
            return True
        elif choice in ['n', 'não', 'nao']:
            return False
        else:
            print(Style.BRIGHT + Fore.RED + "Opção inválida. Digite 's' para Sim ou 'n' para Não.")


def print_banner():
    clear_screen()
    try:
        ascii_art = pyfiglet.figlet_format("PMB AnyDesk Reset", font="slant")
        print(Style.BRIGHT + Fore.GREEN + ascii_art)
    except:
        print(Style.BRIGHT + Fore.MAGENTA + "---PMB AnyDesk Reset ---\n")

    print(Style.BRIGHT + Fore.CYAN + "Criado por: spiro-m4th | Versão PT-BR")
    print(Style.BRIGHT + Fore.YELLOW + "ATENÇÃO: Execute como Administrador para funcionar corretamente.")
    print(Style.BRIGHT + Fore.MAGENTA + "=" * 60 + "\n")


# --- Funções do AnyDesk ---

def find_anydesk_installation_path():
    """Busca o caminho de instalação do AnyDesk."""
    possible_keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]

    found_paths = []
    logger.info("Procurando instalação do AnyDesk...")

    # Busca no Registro
    for hive, key_path in possible_keys:
        try:
            with winreg.OpenKey(hive, key_path) as main_key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(main_key, i)
                        subkey_path = f"{key_path}\\{subkey_name}"
                        with winreg.OpenKey(hive, subkey_path) as sub_key:
                            try:
                                display_name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                                if "anydesk" in display_name.lower():
                                    install_loc = winreg.QueryValueEx(sub_key, "InstallLocation")[0]
                                    if install_loc and os.path.exists(install_loc):
                                        found_paths.append(os.path.normpath(install_loc))
                            except FileNotFoundError:
                                pass
                        i += 1
                    except OSError:
                        break
        except Exception:
            pass

    # Busca em pastas padrão se não achou no registro
    if not found_paths:
        standard_locations = [
            os.path.expandvars(r"%ProgramFiles(x86)%\AnyDesk"),
            os.path.expandvars(r"%ProgramFiles%\AnyDesk"),
        ]
        for loc in standard_locations:
            if os.path.exists(os.path.join(loc, "AnyDesk.exe")):
                found_paths.append(os.path.normpath(loc))

    # Retorna o primeiro encontrado
    found_paths = list(set(found_paths))
    if found_paths:
        return found_paths[0]
    return None


def killing_anydesk():
    """Mata o processo e para o serviço."""
    print(Style.BRIGHT + Fore.LIGHTBLUE_EX + "Parando processos do AnyDesk...")
    logger.info("Executando taskkill...")

    subprocess.run(["taskkill", "/IM", "AnyDesk.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(Style.BRIGHT + Fore.LIGHTBLUE_EX + "Parando serviço do AnyDesk...")
    try:
        subprocess.run(["sc", "stop", "AnyDesk"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["sc", "stop", "AnyDeskService"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)  # Aguarda um pouco
        print(Style.BRIGHT + Fore.GREEN + "Processos e serviços parados (ou já estavam parados).")
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + f"Erro ao parar serviço: {e}")


def run_anydesk():
    """Roda o AnyDesk."""
    print(Style.BRIGHT + Fore.LIGHTBLUE_EX + "Iniciando AnyDesk...")
    install_dir = find_anydesk_installation_path()

    path_to_run = None
    if install_dir:
        path_to_run = os.path.join(install_dir, "AnyDesk.exe")

    if not path_to_run or not os.path.exists(path_to_run):
        # Tenta achar no path padrão se a busca falhou
        default_path = os.path.expandvars(r"%ProgramFiles(x86)%\AnyDesk\AnyDesk.exe")
        if os.path.exists(default_path):
            path_to_run = default_path

    if path_to_run and os.path.exists(path_to_run):
        try:
            subprocess.Popen([path_to_run])
            print(Style.BRIGHT + Fore.GREEN + "AnyDesk iniciado com sucesso.")
        except Exception as e:
            print(Style.BRIGHT + Fore.RED + f"Erro ao iniciar: {e}")
    else:
        print(Style.BRIGHT + Fore.RED + "Executável do AnyDesk não encontrado.")


def remove_anydesk_files(confirm=True):
    """Remove pastas e arquivos para limpeza profunda."""
    print(Style.BRIGHT + Fore.LIGHTBLUE_EX + "Iniciando limpeza profunda...")

    data_paths = [
        os.path.expandvars(r"%PROGRAMDATA%\AnyDesk"),
        os.path.expandvars(r"%APPDATA%\AnyDesk"),
        os.path.expandvars(r"%LOCALAPPDATA%\AnyDesk"),
    ]

    if confirm:
        if not ask_yes_no("ATENÇÃO: Isso apagará TODOS os arquivos de configuração, histórico e ID. Continuar?"):
            return

    killing_anydesk()

    for path in data_paths:
        if os.path.exists(path):
            try:
                shutil.rmtree(path, ignore_errors=True)
                print(Style.BRIGHT + Fore.GREEN + f"Removido: {path}")
            except Exception as e:
                print(Style.BRIGHT + Fore.RED + f"Erro ao remover {path}: {e}")
        else:
            print(Style.BRIGHT + Fore.YELLOW + f"Não encontrado: {path}")


# --- Download e Instalação ---

def download_and_install():
    url = "https://download.anydesk.com/AnyDesk.exe"
    save_path = os.path.join(os.environ["TEMP"], "AnyDesk_Installer.exe")

    print(Style.BRIGHT + Fore.CYAN + "Baixando a versão mais recente...")
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(save_path, 'wb') as file, tqdm(
                desc="Download",
                total=total_size,
                unit='iB', unit_scale=True, unit_divisor=1024,
                ncols=70
        ) as bar:
            for data in response.iter_content(1024):
                size = file.write(data)
                bar.update(size)

        print(Style.BRIGHT + Fore.GREEN + "Download concluído.")

        if ask_yes_no("Deseja instalar agora?"):
            subprocess.run(
                [save_path, "--install", os.path.expandvars(r"%ProgramFiles(x86)%\AnyDesk"), "--start-with-win",
                 "--create-desktop-icon"])
            print(Style.BRIGHT + Fore.GREEN + "Comando de instalação enviado.")

    except Exception as e:
        print(Style.BRIGHT + Fore.RED + f"Erro no download/instalação: {e}")


# --- Menu Principal ---

def main_menu():
    while True:
        print_banner()
        print(f"{Fore.CYAN}1. {Fore.WHITE}Trocar ID do AnyDesk (Reset Rápido)")
        print(f"{Fore.CYAN}2. {Fore.WHITE}Backup e Restauração")
        print(f"{Fore.CYAN}3. {Fore.WHITE}Limpeza Completa (Remove configs e histórico)")
        print(f"{Fore.CYAN}4. {Fore.WHITE}Baixar e Instalar AnyDesk")
        print(f"{Fore.CYAN}5. {Fore.WHITE}Perguntas Frequentes (FAQ)")
        print(f"{Fore.CYAN}0. {Fore.WHITE}Sair")
        print("\n" + Style.BRIGHT + Fore.MAGENTA + "=" * 60)

        choice = input(Style.BRIGHT + Fore.YELLOW + "Escolha uma opção: ").strip()

        if choice == '1':
            killing_anydesk()
            if change_id():
                run_anydesk()
            input(Style.BRIGHT + Fore.BLACK + Back.WHITE + " Pressione Enter para voltar... ")

        elif choice == '2':
            # Submenu Backup
            while True:
                print_banner()
                print(f"{Fore.MAGENTA}--- Menu de Backup e Restauração ---")
                print("1. Fazer Backup das Configurações (user.conf)")
                print("2. Restaurar Configurações")
                print("3. Backup de Gravações de Tela")
                print("4. Restaurar Gravações de Tela")
                print("5. Mudar pasta de destino do Backup")
                print("0. Voltar")
                bc = input(Style.BRIGHT + Fore.YELLOW + "Opção: ").strip()
                if bc == '1':
                    backup_user_conf()
                elif bc == '2':
                    restore_user_conf_interactive()
                elif bc == '3':
                    backup_screen_recordings()
                elif bc == '4':
                    restore_screen_recordings()
                elif bc == '5':
                    set_backup_location_interactive()
                elif bc == '0':
                    break
                input(Style.BRIGHT + Fore.BLACK + Back.WHITE + " Pressione Enter para continuar... ")

        elif choice == '3':
            remove_anydesk_files(confirm=True)
            input(Style.BRIGHT + Fore.BLACK + Back.WHITE + " Pressione Enter para voltar... ")

        elif choice == '4':
            download_and_install()
            input(Style.BRIGHT + Fore.BLACK + Back.WHITE + " Pressione Enter para voltar... ")

        elif choice == '5':
            faq.display_faq()
            input(Style.BRIGHT + Fore.BLACK + Back.WHITE + " Pressione Enter para voltar... ")

        elif choice == '0':
            print(Style.BRIGHT + Fore.GREEN + "Saindo... Obrigado!")
            time.sleep(1)
            sys.exit(0)

        else:
            print(Style.BRIGHT + Fore.RED + "Opção inválida!")
            time.sleep(1)


# --- Ponto de Entrada ---
if __name__ == "__main__":
    # Verifica Admin
    if not is_admin():
        print(Style.BRIGHT + Fore.YELLOW + "O script não está rodando como Administrador.")
        print("Tentando reiniciar com privilégios elevados...")
        try:
            # Re-executa o script pedindo permissão de admin
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
        except Exception as e:
            print(Style.BRIGHT + Fore.RED + f"Falha ao elevar privilégios: {e}")
            print("Por favor, clique com o botão direito e selecione 'Executar como Administrador'.")
            input("Pressione Enter para sair...")
            sys.exit(1)

    # Se já é admin, roda o menu
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n" + Style.BRIGHT + Fore.RED + "Interrompido pelo usuário.")
        sys.exit(0)