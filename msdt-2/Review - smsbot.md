## Code Review: smsbot.py

### 1. Code smell: класс main используется как контейнер для функций

Класс `main` не хранит состояние объекта и не используется как полноценный класс. Методы вызываются напрямую через `main.send_sms()`, поэтому здесь лучше использовать обычные функции.

Было:

```python
class main():

    def banner():
        ...

    def send_sms():
        ...
````

Стало:

```python
def banner():
    ...


def send_sms():
    ...


if __name__ == "__main__":
    send_sms()
```

### 2. Нарушение стандартов кодирования: имя класса написано со строчной буквы

Если класс всё же сохраняется, его имя должно быть в стиле `CamelCase`. Имя `main` нарушает PEP8.

Было:

```python
class main():
```

Стало:

```python
class MessageSender:
```

### 3. Слабая обработка аргументов командной строки

Код сразу обращается к `sys.argv[1]`. Если файл запустить без аргументов, программа завершится с ошибкой.

Было:

```python
input_file = sys.argv[1]
```

Стало:

```python
if len(sys.argv) < 2:
    print("[!] CSV file path is required")
    sys.exit(1)

input_file = sys.argv[1]
```

### 4. Отсутствие проверки CSV-строк

Код предполагает, что каждая строка CSV содержит минимум 4 элемента. Если файл повреждён или строка неполная, возникнет `IndexError`.

Было:

```python
user['username'] = row[0]
user['id'] = int(row[1])
user['access_hash'] = int(row[2])
user['name'] = row[3]
```

Стало:

```python
if len(row) < 4:
    continue

user = {
    "username": row[0],
    "id": int(row[1]),
    "access_hash": int(row[2]),
    "name": row[3],
}
```

### 5. Отсутствие проверки пользовательского ввода

Режим отправки сразу приводится к `int`. Если пользователь введёт текст, программа упадёт с `ValueError`.

Было:

```python
mode = int(input(gr+"Input : "+re))
```

Стало:

```python
try:
    mode = int(input(GREEN_COLOR + "Input : " + RED_COLOR))
except ValueError:
    print("[!] Mode must be a number")
    sys.exit(1)
```

### 6. Нарушение DRY: повторяется логика чтения конфигурации

Чтение `config.data` и получение `api_id`, `api_hash`, `phone` повторяется в нескольких файлах проекта. Это лучше вынести в отдельную функцию или модуль.

Было:

```python
cpass = configparser.RawConfigParser()
cpass.read('config.data')
api_id = cpass['cred']['id']
api_hash = cpass['cred']['hash']
phone = cpass['cred']['phone']
```

Стало:

```python
def load_credentials(config_path="config.data"):
    config = configparser.RawConfigParser()
    config.read(config_path)
    return (
        config["cred"]["id"],
        config["cred"]["hash"],
        config["cred"]["phone"],
    )
```

### 7. Слишком широкая обработка исключений

Блок `except Exception as e` перехватывает любые ошибки и просто продолжает цикл. Так можно скрыть серьёзные проблемы: повреждённый CSV, ошибку авторизации, сетевые сбои.

Было:

```python
except Exception as e:
    print(re+"[!] Error:", e)
    print(re+"[!] Trying to continue...")
    continue
```

Стало:

```python
except ValueError as error:
    print(f"[!] Invalid user data: {error}")
    continue
except OSError as error:
    print(f"[!] Network or file error: {error}")
    break
```

### 8. Потенциальная проблема безопасности: произвольная подстановка в сообщение

Сообщение форматируется через `message.format(user['name'])`. Если пользователь введёт строку с фигурными скобками, это может вызвать ошибку форматирования.

Было:

```python
client.send_message(receiver, message.format(user['name']))
```

Стало:

```python
client.send_message(receiver, message.replace("{name}", user["name"]))
```

### 9. Потенциальная проблема стабильности: нет обработки ошибок при получении получателя

`client.get_input_entity(user['username'])` вызывается до блока `try`. Если username некорректный или недоступный, ошибка не будет обработана внутри цикла отправки.

Было:

```python
if mode == 2:
    if user['username'] == "":
        continue
    receiver = client.get_input_entity(user['username'])
```

Стало:

```python
try:
    if mode == 2:
        if not user["username"]:
            continue
        receiver = client.get_input_entity(user["username"])
    elif mode == 1:
        receiver = InputPeerUser(user["id"], user["access_hash"])
    else:
        print("[!] Invalid Mode. Exiting.")
        client.disconnect()
        sys.exit(1)
except Exception as error:
    print(f"[!] Cannot get receiver: {error}")
    continue
```

### 10. Магическое число: время задержки задано глобальной константой без настройки

`SLEEP_TIME = 120` задано в коде и не может быть изменено пользователем без редактирования файла. Лучше передавать задержку через аргумент командной строки или конфигурацию.

Было:

```python
SLEEP_TIME = 120
time.sleep(SLEEP_TIME)
```

Стало:

```python
DEFAULT_SLEEP_TIME = 120

sleep_time = int(input("Delay between messages: ") or DEFAULT_SLEEP_TIME)
time.sleep(sleep_time)
```

### 11. Потенциальная проблема безопасности и этики: массовая рассылка сообщений

Скрипт отправляет одно сообщение всем пользователям из CSV. Это может привести к жалобам, блокировкам и нарушению правил платформы. Нужно добавить явное подтверждение перед запуском рассылки и ограничение количества сообщений.

Было:

```python
for user in users:
    client.send_message(receiver, message.format(user['name']))
```

Стало:

```python
confirm = input("Send messages to all users from the CSV file? (yes/no): ")

if confirm.lower() != "yes":
    print("Sending cancelled.")
    sys.exit(0)

for user in users[:MAX_MESSAGES_PER_RUN]:
    client.send_message(receiver, message.replace("{name}", user["name"]))
```

### 12. Нарушение читаемости: длинная строка с сообщением об ошибке

Длинный `print` с текстом ошибки сложно читать и поддерживать. Лучше разбить сообщение на несколько строк или вынести в переменную.

Было:

```python
print(
    re+"[!] Getting Flood Error from telegram. \n[!] Script is stopping now. \n[!] Please try again after some time.")
```

Стало:

```python
error_message = (
    "[!] Getting Flood Error from Telegram.\n"
    "[!] Script is stopping now.\n"
    "[!] Please try again after some time."
)
print(RED_COLOR + error_message)
```