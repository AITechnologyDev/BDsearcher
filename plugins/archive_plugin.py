import os
import zipfile
import rarfile
from io import TextIOWrapper
from typing import List, Tuple

# Конфигурационные константы
PASSWORD_FILE = "zip_rar_keys.txt"
MAX_RECURSION_DEPTH = 3

def load_passwords() -> dict:
    """Загрузка паролей из файла"""
    passwords = {}
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if ':' in line:
                    archive, pwd = line.strip().split(':', 1)
                    passwords[archive] = pwd
    return passwords

def save_password(archive_path: str, password: str) -> None:
    """Сохранение пароля в файл"""
    with open(PASSWORD_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{archive_path}:{password}\n")

def extract_archive(archive_path: str, password: str = None) -> tuple:
    """Извлечение архива с обработкой ошибок"""
    try:
        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as z:
                if password:
                    z.setpassword(password.encode())
                return True, z.namelist()
        
        elif archive_path.endswith('.rar'):
            with rarfile.RarFile(archive_path, 'r') as r:
                if password:
                    r.setpassword(password)
                return True, r.namelist()
    
    except (zipfile.BadZipFile, rarfile.BadRarFile) as e:
        return False, f"Corrupted archive: {str(e)}"
    except (RuntimeError, rarfile.PasswordRequired) as e:
        return False, "Password required"
    except Exception as e:
        return False, f"Error: {str(e)}"

def search_in_archive(archive_path: str, search_term: str, passwords: dict, depth: int = 0) -> List[Tuple]:
    """Рекурсивный поиск в архивах"""
    results = []
    if depth > MAX_RECURSION_DEPTH:
        return results

    # Получаем пароль из кэша или запрашиваем у пользователя
    password = passwords.get(archive_path)
    if not password and archive_path in passwords:
        from BDSearcher import get_input
        password = get_input(f"Enter password for {os.path.basename(archive_path)}")
        save_password(archive_path, password)

    # Пытаемся открыть архив
    status, content = extract_archive(archive_path, password)
    if not status:
        return [("Archive Error", archive_path, content)]

    # Обрабатываем файлы внутри архива
    try:
        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as z:
                if password:
                    z.setpassword(password.encode())
                
                for file in z.namelist():
                    # Рекурсия для вложенных архивов
                    if file.endswith(('.zip', '.rar')):
                        nested_path = os.path.join(archive_path, file)
                        results += search_in_archive(nested_path, search_term, passwords, depth + 1)
                    
                    # Поиск в текстовых файлах
                    elif file.endswith(('.txt', '.md', '.csv')):
                        with z.open(file) as f:
                            content = TextIOWrapper(f).read()
                            if search_term.lower() in content.lower():
                                results.append((
                                    "ZIP Content",
                                    f"{archive_path}/{file}",
                                    content[:200] + "..."
                                ))

        elif archive_path.endswith('.rar'):
            with rarfile.RarFile(archive_path, 'r') as r:
                if password:
                    r.setpassword(password)
                
                for file in r.namelist():
                    if file.endswith(('.zip', '.rar')):
                        nested_path = os.path.join(archive_path, file)
                        results += search_in_archive(nested_path, search_term, passwords, depth + 1)
                    
                    elif file.endswith(('.txt', '.md', '.csv')):
                        with r.open(file) as f:
                            content = f.read().decode('utf-8', errors='ignore')
                            if search_term.lower() in content.lower():
                                results.append((
                                    "RAR Content",
                                    f"{archive_path}/{file}",
                                    content[:200] + "..."
                                ))
    
    except Exception as e:
        results.append(("Archive Error", archive_path, str(e)))

    return results

def archive_handler(file_path: str, search_term: str) -> List[Tuple]:
    """Основной обработчик архивов"""
    passwords = load_passwords()
    return search_in_archive(file_path, search_term, passwords)

def register(handlers):
    handlers['.zip'] = handlers['.rar'] = {
        'name': 'Archive Search',
        'description': 'Search inside ZIP/RAR archives (supports passwords)',
        'handler': archive_handler
    }