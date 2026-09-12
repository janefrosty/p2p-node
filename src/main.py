import asyncio
import logging
import sys

from transport import Node
import protocol

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("node")

async def handler(conn, msg_type: int, payload: dict):
    if msg_type == protocol.PING:
        log.info(f"PING от {conn.peer}")
        await conn.send(protocol.PONG, {"echo": payload.get("nonce")})

    elif msg_type == protocol.PONG:
        log.info(f"PONG от {conn.peer}: {payload}")

    elif msg_type == protocol.MESSAGE:
        text = payload.get("text", "")
        sender = payload.get("from", "?")
        print(f"\n[{sender}]: {text}")

    else:
        log.warning(f"Неизвестный тип {msg_type} от {conn.peer}")


async def stdin_loop(node: Node):
    loop = asyncio.get_event_loop()
    while True:
        line = await loop.run_in_executor(None, input, "> ")
        parts = line.strip().split(maxsplit=2)
        if not parts:
            continue
        cmd = parts[0]

        if cmd == "quit":
            return

        elif cmd == "ping" and len(parts) == 3:
            conn = await node.connect(parts[1], int(parts[2]))
            await conn.send(protocol.PING, {"nonce": 42})

        elif cmd == "send" and len(parts) == 3:
            addr, text = parts[1], parts[2]
            host, port = addr.split(":")
            conn = await node.connect(host, int(port))
            await conn.send(protocol.MESSAGE, {
                "from": f"node-{node.port}",
                "text": text,
            })

        else:
            print("Команды:")
            print("  ping <host> <port>         — проверить узел")
            print("  send <host:port> <text>    — отправить сообщение")
            print("  quit                       — выйти")


async def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    node = Node(port, handler)
    await node.start()
    print(f"Узел запущен на порту {port}.")
    try:
        await stdin_loop(node)
    finally:
        await node.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass