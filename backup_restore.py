import os
import shutil
import logging
import sys
import zipfile
from colorama import init, Fore, Style
import tkinter as tk
from tkinter import filedialog

# Inicializa o colorama
init(autoreset=True)
logger = logging.getLogger(__name__)

# --- Constantes e Variáveis Globais ---
USER_CONF_PATH = os.path.expandvars(r"%APPDATA%\AnyDesk\user.conf")
DEFAULT_BACKUP_DIR = os.path.expanduser("~/Desktop")
_backup_filename = "user.conf.backup"
DEFAULT_RECORDINGS_DIR = os.path.join(os.path.expanduser("~"), "Videos", "AnyDesk", "screen recordings")
RECORDINGS_BACKUP_FILENAME_BASE = "AnyDesk_Screen_Recordings_Backup"

_current_backup_dir = DEFAULT_BACKUP_DIR


# --- Funções para gerenciar o caminho de backup ---

def get_current_backup_path():
    """Retorna o caminho completo para o arquivo de backup user.conf no diretório selecionado."""
    return os.path.join(_current_backup_dir, _backup_filename)


def get_current_recordings_backup_path():
    """Retorna o caminho completo para o arquivo de backup das gravações (.zip) no diretório selecionado."""
    return os.path.join(_current_backup_dir, RECORDINGS_BACKUP_FILENAME_BASE + ".zip")


def set_backup_location_interactive():
    """Solicita interativamente ao usuário uma nova pasta para backups."""
    global _current_backup_dir
    print(Style.BRIGHT + Fore.CYAN + f"Pasta de backup atual: {Fore.YELLOW}{_current_backup_dir}")
    logger.info(f"Pasta de backup atual: {_current_backup_dir}")

    while True:
        choice = input(
            Style.BRIGHT + Fore.CYAN + "Deseja alterar a pasta onde os backups sao salvos? (s/n): ").strip().lower()
        if choice in ['s', 'n', 'y']:  # Aceita 'y' por compatibilidade
            break
        else:
            print(Style.BRIGHT + Fore.RED + "Opcao invalida. Digite 's' para sim ou 'n' para nao.")
            logger.warning("Entrada inválida ao escolher pasta de backup.")

    if choice == 's' or choice == 'y':
        logger.info("Usuario optou por alterar a pasta de backup.")
        print(Style.BRIGHT + Fore.YELLOW + "Por favor, selecione a nova pasta na janela que abrirá...")
        root = tk.Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        selected_dir = filedialog.askdirectory(
            title="Selecione a pasta para salvar os backups",
            initialdir=_current_backup_dir
        )
        root.destroy()

        if selected_dir:
            logger.info(f"Usuário selecionou a pasta: {selected_dir}")
            if os.access(selected_dir, os.W_OK):
                _current_backup_dir = selected_dir
                print(Style.BRIGHT + Fore.GREEN + f"Nova pasta de backup definida: {Fore.YELLOW}{_current_backup_dir}")
                logger.info(f"Nova pasta de backup definida: {_current_backup_dir}")
            else:
                print(Style.BRIGHT + Fore.RED + f"Sem permissao de escrita na pasta: {selected_dir}")
                print(Style.BRIGHT + Fore.YELLOW + "A pasta de backup não foi alterada.")
                logger.error(f"Sem permissao de escrita em '{selected_dir}'. Pasta não alterada.")
        else:
            print(Style.BRIGHT + Fore.YELLOW + "Selecao de pasta cancelada.")
            logger.info("Selecao de pasta cancelada pelo usuário.")
    else:
        print(Style.BRIGHT + Fore.GREEN + "Pasta de backup mantida.")
        logger.info("Usuário manteve a pasta de backup atual.")


# --- Funções principais de Backup e Restauração ---

def backup_user_conf():
    """Cria um backup do arquivo user.conf."""
    backup_path = get_current_backup_path()
    backup_dir = os.path.dirname(backup_path)
    conf_filename = os.path.basename(USER_CONF_PATH)

    print(
        Style.BRIGHT + Fore.CYAN + f"Iniciando backup de {Fore.YELLOW}{conf_filename}{Fore.CYAN} para {Fore.YELLOW}{backup_path}{Fore.CYAN}...")
    logger.info(f"Iniciando backup de {conf_filename} para {backup_path}")

    if not os.path.exists(USER_CONF_PATH):
        print(Style.BRIGHT + Fore.YELLOW + f"Arquivo original {USER_CONF_PATH} não encontrado. Backup ignorado.")
        logger.warning(f"Arquivo fonte {USER_CONF_PATH} não encontrado, backup pulado.")
        return

    try:
        os.makedirs(backup_dir, exist_ok=True)
        shutil.copy2(USER_CONF_PATH, backup_path)  # copy2 preserva metadados
        print(
            Style.BRIGHT + Fore.GREEN + f"Backup de {conf_filename} concluído com sucesso em: {Fore.YELLOW}{backup_path}")
        logger.info(f"Backup de {conf_filename} criado/atualizado com sucesso: {backup_path}")
    except PermissionError:
        print(Style.BRIGHT + Fore.RED + f"Erro de permissao ao criar backup na pasta: {backup_dir}")
        print(Style.BRIGHT + Fore.YELLOW + "Tente rodar o script como Administrador ou escolha outra pasta.")
        logger.error(f"Erro de permissao ao criar backup em '{backup_dir}'.")
    except OSError as e:
        print(
            Style.BRIGHT + Fore.RED + f"Erro de sistema ao criar backup em {backup_path}: {e.strerror} (Erro {e.errno})")
        logger.error(f"Erro de sistema ao criar backup de {conf_filename} em '{backup_path}': {e}", exc_info=True)
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + f"Erro inesperado: {e}", file=sys.stderr)
        logger.exception(f"Erro inesperado ao criar backup de {conf_filename}: {e}")


def restore_user_conf_interactive():
    """Restaura o user.conf de forma interativa."""
    current_default_backup = get_current_backup_path()
    target_dir = os.path.dirname(USER_CONF_PATH)
    conf_filename = os.path.basename(USER_CONF_PATH)

    print(
        Style.BRIGHT + Fore.CYAN + f"Iniciando restauracao de {Fore.YELLOW}{conf_filename}{Fore.CYAN} para {Fore.YELLOW}{target_dir}{Fore.CYAN}...")
    logger.info(f"Iniciando restauracao interativa de {conf_filename} para {target_dir}")

    while True:
        print(Style.BRIGHT + Fore.CYAN + "De onde você deseja restaurar o arquivo?")
        print(
            Style.BRIGHT + Fore.LIGHTYELLOW_EX + f"1. Da pasta de backup atual ({Fore.YELLOW}{_current_backup_dir}{Style.BRIGHT + Fore.LIGHTYELLOW_EX})")
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + "2. Selecionar um arquivo manualmente (.conf ou .backup)")
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + "3. Cancelar")

        choice = input(Style.BRIGHT + Fore.CYAN + "Digite sua escolha (1, 2 ou 3): ").strip()
        logger.debug(f"Usuário escolheu opcao de restauracao: {choice}")

        if choice not in ['1', '2', '3']:
            print(Style.BRIGHT + Fore.RED + "Opcao inválida. Escolha 1, 2 ou 3.")
            logger.warning("Entrada inválida no menu de restauracao.")
            continue

        backup_source = None
        if choice == '1':
            backup_source = current_default_backup
            if not os.path.exists(backup_source):
                print(
                    Style.BRIGHT + Fore.RED + f"Arquivo de backup padrao não encontrado em: {Fore.YELLOW}{backup_source}")
                print(Style.BRIGHT + Fore.YELLOW + "Tente a opcao manual.")
                logger.warning(f"Backup padrao não encontrado: {backup_source}")
                backup_source = None
                continue

        elif choice == '2':
            logger.info("Usuário escolheu selecionar arquivo manualmente.")
            print(Style.BRIGHT + Fore.YELLOW + "Abrindo janela de selecao...")
            root = tk.Tk()
            root.attributes('-topmost', True)
            root.withdraw()
            selected_file = filedialog.askopenfilename(
                title="Selecione o arquivo de backup do user.conf",
                filetypes=[("Arquivos de Configuracao/Backup", "*.conf *.backup"), ("Todos os Arquivos", "*.*")],
                initialdir=_current_backup_dir
            )
            root.destroy()

            if selected_file:
                backup_source = selected_file
                logger.info(f"Usuário selecionou o arquivo: {backup_source}")
            else:
                print(Style.BRIGHT + Fore.YELLOW + "Nenhum arquivo selecionado. Retornando ao menu.")
                logger.info("Selecao de arquivo cancelada.")
                continue

        elif choice == '3':
            print(Style.BRIGHT + Fore.YELLOW + "Restauracao cancelada.")
            logger.info("Restauracao cancelada pelo usuário.")
            return

        if backup_source:
            print(
                Style.BRIGHT + Fore.GREEN + f"Arquivo selecionado: '{Fore.YELLOW}{backup_source}{Style.BRIGHT + Fore.GREEN}'")
            logger.info(f"Tentando restaurar {conf_filename} de {backup_source}")
            try:
                os.makedirs(target_dir, exist_ok=True)
                shutil.copy2(backup_source, USER_CONF_PATH)
                print(
                    Style.BRIGHT + Fore.GREEN + f"Sucesso! Arquivo {Fore.YELLOW}{conf_filename}{Style.BRIGHT + Fore.GREEN} restaurado para {Fore.YELLOW}{target_dir}{Style.BRIGHT + Fore.GREEN}.")
                logger.info(f"{conf_filename} restaurado com sucesso de {backup_source} para {target_dir}.")
                return
            except FileNotFoundError:
                print(Style.BRIGHT + Fore.RED + f"Erro: O arquivo fonte '{backup_source}' nao foi encontrado.")
                logger.error(f"Arquivo fonte '{backup_source}' nao encontrado durante a restauracao.")
                return
            except PermissionError:
                print(
                    Style.BRIGHT + Fore.RED + f"Erro de permissao ao copiar de '{backup_source}' para '{target_dir}'.")
                logger.error(f"Erro de permissao na restauracao.")
                return
            except shutil.SameFileError:
                print(
                    Style.BRIGHT + Fore.YELLOW + "O arquivo de origem e destino são o mesmo. Nenhuma alteração feita.")
                logger.warning("Origem e destino são identicos.")
                return
            except OSError as e:
                print(Style.BRIGHT + Fore.RED + f"Erro de sistema: {e.strerror} (Erro {e.errno})")
                logger.error(f"Erro de sistema na restauracao: {e}", exc_info=True)
                return
            except Exception as e:
                print(Style.BRIGHT + Fore.RED + f"Erro inesperado: {e}", file=sys.stderr)
                logger.exception(f"Erro inesperado na restauracao: {e}")
                return


def restore_user_conf_default():
    """Tenta restaurar o user.conf automaticamente da pasta de backup atual (não interativo)."""
    backup_path = get_current_backup_path()
    target_dir = os.path.dirname(USER_CONF_PATH)
    conf_filename = os.path.basename(USER_CONF_PATH)

    print(
        Style.BRIGHT + Fore.CYAN + f"Tentando restauracao automática de {Fore.YELLOW}{conf_filename}{Fore.CYAN} a partir de '{Fore.YELLOW}{backup_path}{Fore.CYAN}'...")
    logger.info(f"Tentativa de restauracao automática de {conf_filename} a partir de {backup_path}")

    if not os.path.exists(backup_path):
        print(
            Style.BRIGHT + Fore.YELLOW + f"Backup nao encontrado em '{backup_path}'. Restauracao automática cancelada.")
        logger.warning(f"Backup não encontrado em '{backup_path}'.")
        return

    try:
        os.makedirs(target_dir, exist_ok=True)
        shutil.copy2(backup_path, USER_CONF_PATH)
        print(Style.BRIGHT + Fore.GREEN + "Restauracao automática concluída com sucesso.")
        logger.info(f"Restauracao automática de {conf_filename} concluída.")
    except FileNotFoundError:
        print(Style.BRIGHT + Fore.RED + f"Arquivo '{backup_path}' sumiu durante o processo.")
        logger.error(f"Arquivo '{backup_path}' não encontrado durante restauracao auto.")
    except PermissionError:
        print(Style.BRIGHT + Fore.RED + f"Erro de permissao ao restaurar para '{target_dir}'.")
        logger.error(f"Erro de permissao na restauracao auto.")
    except shutil.SameFileError:
        print(Style.BRIGHT + Fore.YELLOW + "Arquivos identicos. Ignorado.")
    except OSError as e:
        print(Style.BRIGHT + Fore.RED + f"Erro de sistema: {e.strerror}")
        logger.error(f"Erro de sistema na restauracao auto: {e}", exc_info=True)
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + f"Erro inesperado: {e}", file=sys.stderr)
        logger.exception(f"Erro inesperado na restauracao auto: {e}")


def select_directory(prompt_title, initial_dir=None):
    """Função auxiliar para seleção de diretório."""
    print(Style.BRIGHT + Fore.YELLOW + prompt_title)
    logger.info(f"Solicitando diretório: {prompt_title}")
    root = tk.Tk()
    root.attributes('-topmost', True)
    root.withdraw()
    selected_dir = filedialog.askdirectory(title=prompt_title, initialdir=initial_dir)
    root.destroy()
    if not selected_dir:
        print(Style.BRIGHT + Fore.YELLOW + "Nenhuma pasta selecionada.")
        logger.info("Seleção de pasta cancelada.")
    else:
        logger.info(f"Pasta selecionada: {selected_dir}")
    return selected_dir


def backup_screen_recordings():
    """Cria um arquivo ZIP com as gravações de tela do AnyDesk."""
    print(Style.BRIGHT + Fore.MAGENTA + "=== Backup de Gravacoes de Tela ===")
    logger.info("Iniciando backup de gravacoes de tela.")

    # 1. Definir pasta de origem
    recordings_source_dir = None
    print(f"Caminho padrao das gravacoes: {Fore.YELLOW}{DEFAULT_RECORDINGS_DIR}")
    logger.debug(f"Caminho padrao gravacoes: {DEFAULT_RECORDINGS_DIR}")

    while True:
        choice = input(
            Style.BRIGHT + Fore.CYAN + "Onde estão as gravacoes? (d=Padrao / c=Escolher pasta): ").strip().lower()
        if choice == 'd':
            recordings_source_dir = DEFAULT_RECORDINGS_DIR
            if not os.path.isdir(recordings_source_dir):
                print(Style.BRIGHT + Fore.RED + f"A pasta padrao não existe: {recordings_source_dir}")
                print(Style.BRIGHT + Fore.YELLOW + "Backup cancelado.")
                logger.error(f"Pasta padrao de gravacoes não encontrada: {recordings_source_dir}")
                return
            break
        elif choice == 'c':
            recordings_source_dir = select_directory("Selecione a pasta onde estão as gravacoes",
                                                     os.path.dirname(DEFAULT_RECORDINGS_DIR))
            if not recordings_source_dir:
                logger.info("Backup cancelado (sem pasta de origem).")
                return
            if not os.path.isdir(recordings_source_dir):
                print(Style.BRIGHT + Fore.RED + f"A pasta selecionada é inválida: {recordings_source_dir}")
                return
            break
        else:
            print(Style.BRIGHT + Fore.RED + "Opção inválida. Digite 'd' para Padrao ou 'c' para Escolher.")

    print(f"Pasta de origem definida: {Fore.YELLOW}{recordings_source_dir}")
    logger.info(f"Origem das gravacoes: {recordings_source_dir}")

    try:
        # Verifica se está vazia
        if not os.listdir(recordings_source_dir):
            print(Style.BRIGHT + Fore.YELLOW + "A pasta de gravacoes está vazia. Nada para salvar.")
            logger.warning("Pasta de gravacoes vazia.")
            return
    except FileNotFoundError:
        print(Style.BRIGHT + Fore.RED + f"A pasta '{recordings_source_dir}' não foi encontrada.")
        return
    except OSError as e:
        print(Style.BRIGHT + Fore.RED + f"Erro de acesso à pasta: {e.strerror}")
        return

    # 2. Definir arquivo de destino (ZIP)
    backup_archive_base = os.path.join(_current_backup_dir, RECORDINGS_BACKUP_FILENAME_BASE)
    backup_archive_path = backup_archive_base + ".zip"
    print(f"O arquivo será salvo em: {Fore.YELLOW}{backup_archive_path}")
    logger.info(f"Destino do arquivo ZIP: {backup_archive_path}")

    if os.path.exists(backup_archive_path):
        print(
            Style.BRIGHT + Fore.YELLOW + f"O arquivo '{os.path.basename(backup_archive_path)}' já existe na pasta de backup.")
        logger.warning(f"Arquivo ZIP já existe: {backup_archive_path}")
        resp = input(Style.BRIGHT + Fore.CYAN + "Deseja sobrescrever o arquivo existente? (s/n): ").strip().lower()
        if resp != 's' and resp != 'y':
            print(Style.BRIGHT + Fore.YELLOW + "Backup cancelado pelo usuário.")
            return
        logger.info("Sobrescrita confirmada.")

    # 3. Criar arquivo ZIP
    try:
        print(Style.BRIGHT + Fore.YELLOW + "Compactando arquivos (isso pode demorar)...")
        logger.info("Criando ZIP...")
        os.makedirs(os.path.dirname(backup_archive_path), exist_ok=True)
        shutil.make_archive(base_name=backup_archive_base,
                            format='zip',
                            root_dir=recordings_source_dir)
        print(Style.BRIGHT + Fore.GREEN + f"Backup de gravações criado com sucesso: {Fore.YELLOW}{backup_archive_path}")
        logger.info(f"ZIP criado com sucesso: {backup_archive_path}")
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + f"Erro inesperado ao criar ZIP: {e}", file=sys.stderr)
        logger.exception(f"Erro ao criar ZIP: {e}")


def restore_screen_recordings():
    """Restaura gravações de tela a partir de um ZIP."""
    print(Style.BRIGHT + Fore.MAGENTA + "=== Restaurar Gravações de Tela ===")
    logger.info("Iniciando restauração de gravações.")

    # 1. Definir arquivo ZIP de origem
    backup_archive_path = None
    default_backup_path = get_current_recordings_backup_path()
    print(f"Caminho padrão do backup: {Fore.YELLOW}{default_backup_path}")

    while True:
        choice = input(
            Style.BRIGHT + Fore.CYAN + "Qual arquivo usar? (d=Padrão / c=Escolher arquivo): ").strip().lower()
        if choice == 'd':
            backup_archive_path = default_backup_path
            if not os.path.isfile(backup_archive_path):
                print(Style.BRIGHT + Fore.RED + f"Arquivo padrão não encontrado: {backup_archive_path}")
                print(Style.BRIGHT + Fore.YELLOW + "Cancelado.")
                return
            break
        elif choice == 'c':
            print(Style.BRIGHT + Fore.YELLOW + "Selecione o arquivo ZIP...")
            root = tk.Tk();
            root.attributes('-topmost', True);
            root.withdraw()
            selected_file = filedialog.askopenfilename(
                title="Selecione o arquivo ZIP de backup das gravações",
                filetypes=[("Arquivos ZIP", "*.zip"), ("Todos os arquivos", "*.*")],
                initialdir=_current_backup_dir
            )
            root.destroy()
            if not selected_file:
                print(Style.BRIGHT + Fore.YELLOW + "Nenhum arquivo selecionado.");
                return
            if not os.path.isfile(selected_file):
                print(Style.BRIGHT + Fore.RED + "Arquivo inválido.");
                return
            backup_archive_path = selected_file
            break
        else:
            print(Style.BRIGHT + Fore.RED + "Opção inválida (d/c).")

    print(f"Usando arquivo: {Fore.YELLOW}{backup_archive_path}")
    logger.info(f"Arquivo ZIP selecionado: {backup_archive_path}")

    # 2. Definir pasta de destino
    restore_destination_dir = None
    print(f"Pasta padrão de destino: {Fore.YELLOW}{DEFAULT_RECORDINGS_DIR}")

    while True:
        choice = input(Style.BRIGHT + Fore.CYAN + "Onde descompactar? (d=Padrão / c=Escolher pasta): ").strip().lower()
        if choice == 'd':
            restore_destination_dir = DEFAULT_RECORDINGS_DIR
            break
        elif choice == 'c':
            restore_destination_dir = select_directory("Selecione a pasta de destino para as gravações",
                                                       os.path.dirname(DEFAULT_RECORDINGS_DIR))
            if not restore_destination_dir: return
            break
        else:
            print(Style.BRIGHT + Fore.RED + "Opção inválida (d/c).")

    print(f"Destino: {Fore.YELLOW}{restore_destination_dir}")
    logger.info(f"Pasta destino: {restore_destination_dir}")

    # 3. Validar pasta destino e descompactar
    try:
        should_warn = False
        if os.path.exists(restore_destination_dir):
            if any(os.path.isfile(os.path.join(restore_destination_dir, i)) for i in
                   os.listdir(restore_destination_dir)):
                should_warn = True
        else:
            os.makedirs(restore_destination_dir, exist_ok=True)

        if should_warn:
            print(Style.BRIGHT + Fore.YELLOW + f"Aviso: A pasta '{restore_destination_dir}' não está vazia.")
            print(Style.BRIGHT + Fore.YELLOW + "Arquivos existentes podem ser sobrescritos.")
            resp = input(Style.BRIGHT + Fore.CYAN + "Deseja continuar? (s/n): ").strip().lower()
            if resp != 's' and resp != 'y':
                print(Style.BRIGHT + Fore.YELLOW + "Cancelado.")
                return

    except OSError as e:
        print(Style.BRIGHT + Fore.RED + f"Erro ao acessar pasta de destino: {e.strerror}")
        return

    # 4. Descompactar
    try:
        print(Style.BRIGHT + Fore.YELLOW + "Descompactando...")
        shutil.unpack_archive(filename=backup_archive_path,
                              extract_dir=restore_destination_dir,
                              format='zip')
        print(
            Style.BRIGHT + Fore.GREEN + f"Gravações restauradas com sucesso em: {Fore.YELLOW}{restore_destination_dir}")
        logger.info("Descompactação concluída.")
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + f"Erro ao descompactar: {e}", file=sys.stderr)
        logger.exception(f"Erro na descompactação: {e}")


# --- Ponto de entrada para testes (Modo Standalone) ---
if __name__ == "__main__":
    # Configuração básica de log para teste
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logger.info("Iniciando backup_restore em modo teste.")

    print(Style.BRIGHT + Fore.MAGENTA + "=== MODO DE TESTE BACKUP/RESTORE (PT-BR) ===")
    while True:
        print(Style.BRIGHT + Fore.CYAN + "\n--- Menu de Teste ---")
        print(Style.BRIGHT + Fore.BLUE + f"Pasta Atual de Backup: {Fore.YELLOW}{_current_backup_dir}")
        print(Style.BRIGHT + Fore.GREEN + "   [Configuração user.conf]")
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + "1. Fazer Backup")
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + "2. Restaurar")
        print(Style.BRIGHT + Fore.GREEN + "   [Gravações de Tela]")
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + "3. Fazer Backup")
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + "4. Restaurar")
        print(Style.BRIGHT + Fore.GREEN + "   [Configurações]")
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + "5. Alterar pasta de Backup")
        print(Style.BRIGHT + Fore.LIGHTRED_EX + "6. Sair")

        choice = input(Style.BRIGHT + Fore.CYAN + "Escolha uma opção (1-6): ").strip()

        if choice == '1':
            backup_user_conf()
        elif choice == '2':
            restore_user_conf_interactive()
        elif choice == '3':
            backup_screen_recordings()
        elif choice == '4':
            restore_screen_recordings()
        elif choice == '5':
            set_backup_location_interactive()
        elif choice == '6':
            print("Saindo do modo de teste.")
            break
        else:
            print("Opção inválida.")

        if sys.stdin.isatty():
            input("Pressione Enter para continuar...")