### 1. Нарушение стандартов кодирования: импорты расположены не в начале файла

Импорты должны находиться в начале файла, после shebang и комментариев. Сейчас переменные цветов объявлены до импортов.

Было:

```python
re="\033[1;31m"
gr="\033[1;32m"
cy="\033[1;36m"

import os, sys
import time
````

Стало:

```python
import os
import sys
import time

RED_COLOR = "\033[1;31m"
GREEN_COLOR = "\033[1;32m"
CYAN_COLOR = "\033[1;36m"
```

### 2. Небезопасное выполнение shell-команд через `os.system`

В коде используются shell-команды для установки пакетов, удаления файлов и изменения прав. Это небезопасно и плохо контролируется.

Было:

```python
os.system("""
    pip3 install telethon requests configparser
    python3 -m pip install telethon requests configparser
    touch config.data
    """)
```

Стало:

```python
import subprocess

subprocess.run(
    [sys.executable, "-m", "pip", "install", "telethon", "requests", "configparser"],
    check=True,
)
open("config.data", "a", encoding="utf-8").close()
```

### 3. Потенциально опасное удаление файлов

Команда `rm *.py` удаляет все Python-файлы в текущей папке. При ошибочном запуске можно потерять пользовательские файлы.

Было:

```python
os.system('rm *.py')
```

Стало:

```python
from pathlib import Path

for file_path in Path(".").glob("*.py"):
    if file_path.name in {"scraper.py", "setup.py", "smsbot.py"}:
        file_path.unlink()
```

### 4. Нарушение DRY: повторяется код вывода выбранного модуля

Одинаковый `print(...)` повторяется в нескольких ветках условий. Лучше вынести его в отдельную функцию.

Было:

```python
print(gr+'['+cy+'+'+gr+']'+cy+' selected module : '+re+sys.argv[1])
config_setup()
```

Стало:

```python
def print_selected_module(argument):
    print(f"{GREEN_COLOR}[{CYAN_COLOR}+{GREEN_COLOR}]{CYAN_COLOR} selected module: {RED_COLOR}{argument}")

print_selected_module(sys.argv[1])
config_setup()
```

### 5. Слабая обработка аргументов командной строки

Код вручную обращается к `sys.argv[1]`, из-за чего при отсутствии аргументов возникает `IndexError`. Для таких задач лучше использовать `argparse`.

Было:

```python
try:
    if any ([sys.argv[1] == '--config', sys.argv[1] == '-c']):
        config_setup()
except IndexError:
    print('no argument given')
```

Стало:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", action="store_true")
parser.add_argument("-m", "--merge", nargs=2)
parser.add_argument("-u", "--update", action="store_true")
parser.add_argument("-i", "--install", action="store_true")

args = parser.parse_args()
```

### 6. Логическая ошибка в обработчике `IndexError`

В блоке `except IndexError` снова используется `sys.argv[1]`, хотя именно его отсутствие и вызвало ошибку.

Было:

```python
except IndexError:
    print('\n'+gr+'['+re+'!'+gr+']'+cy+' no argument given : '+ sys.argv[1])
```

Стало:

```python
except IndexError:
    print(f"\n{GREEN_COLOR}[{RED_COLOR}!{GREEN_COLOR}]{CYAN_COLOR} no argument given")
```

### 7. Отсутствие проверки количества аргументов для merge

Функция `merge_csv()` использует `sys.argv[2]` и `sys.argv[3]`, но перед этим не проверяется, что пользователь действительно передал два файла.

Было:

```python
file1 = pd.read_csv(sys.argv[2])
file2 = pd.read_csv(sys.argv[3])
```

Стало:

```python
if len(sys.argv) < 4:
    print("[!] two CSV files are required")
    sys.exit(1)

file1 = pd.read_csv(sys.argv[2])
file2 = pd.read_csv(sys.argv[3])
```

### 8. Небезопасное обновление программы из внешнего источника

Функция `update_tool()` скачивает файлы через `curl` и заменяет локальные `.py`-файлы без проверки целостности и подтверждения пользователя.

Было:

```python
os.system("""
    curl -s -O https://raw.githubusercontent.com/th3unkn0n/TeleGram-Scraper/master/setup.py
    chmod 777 *.py
    """)
```

Стало:

```python
print("[!] Automatic self-update is disabled for security reasons.")
print("[!] Please download updates manually from the official repository.")
```

### 9. Нарушение принципа единственной ответственности

Файл `setup.py` одновременно устанавливает зависимости, пишет конфиг, объединяет CSV и обновляет программу. Это усложняет поддержку.

Было:

```python
def requirements():
    ...

def config_setup():
    ...

def merge_csv():
    ...

def update_tool():
    ...
```

Стало:

```python
# install.py
def install_requirements():
    ...

# config.py
def create_config():
    ...

# csv_tools.py
def merge_csv_files(file_a, file_b):
    ...
```

### 10. Небезопасное хранение чувствительных данных

API ID, hash и номер телефона сохраняются в обычный файл `config.data`. Лучше использовать переменные окружения или хотя бы исключить файл из Git.

Было:

```python
cpass.set('cred', 'id', xid)
cpass.set('cred', 'hash', xhash)
cpass.set('cred', 'phone', xphone)
```

Стало:

```python
import os

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
phone = os.getenv("TELEGRAM_PHONE")
```