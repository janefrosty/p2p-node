# P2P Node

Прототип узла P2P-сети поверх TCP/IP.
Курсовая работа, Этап 1: транспортный уровень.

## Первый этап:

- TCP-сервер и TCP-клиент на asyncio.
- Собственный формат кадра: `[длина][тип][payload]`.
- Сериализация payload через msgpack.
- Диспетчер сообщений по типу.
- Простые команды из stdin для проверки: `ping`, `send`, `quit`.

## Используется:

- Ubuntu 22.04 
- Python 3.10+.

## Установка

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

git clone <repo-url> p2p-node
cd p2p-node
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Запуск

Терминал 1:
```bash
source venv/bin/activate
python src/main.py 8001
```

Терминал 2:
```bash
source venv/bin/activate
python src/main.py 8002
```

## Команды stdin
Команда         	       Что делает
ping <host> <port>	       Отправляет PING указанному узлу
send <host:port> <text>	   Отправляет MESSAGE
quit	                   Завершает работу узла

