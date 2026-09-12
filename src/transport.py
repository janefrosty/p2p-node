import asyncio
import logging

from protocol import encode_frame, read_frame


log = logging.getLogger("transport")


class Connection:
    def __init__(self, reader, writer, peer):
        self.reader = reader
        self.writer = writer
        self.peer = peer  # (host, port)

    async def send(self, msg_type: int, payload: dict):
        self.writer.write(encode_frame(msg_type, payload))
        await self.writer.drain()

    async def recv(self):
        return await read_frame(self.reader)

    async def close(self):
        self.writer.close()
        try:
            await self.writer.wait_closed()
        except Exception:
            pass


class Node:
    def __init__(self, port: int, handler):
        self.port = port
        self.handler = handler
        self.server = None

    async def start(self):
        self.server = await asyncio.start_server(
            self._on_client, "0.0.0.0", self.port
        )
        log.info(f"Узел слушает порт {self.port}")

    async def _on_client(self, reader, writer):
        peer = writer.get_extra_info("peername")
        conn = Connection(reader, writer, peer)
        log.info(f"Входящее соединение от {peer}")
        await self._serve(conn)

    async def _serve(self, conn: Connection):
        while True:
            try:
                msg_type, payload = await conn.recv()
            except (asyncio.IncompleteReadError, ConnectionError):
                break
            except Exception as e:
                log.warning(f"Ошибка чтения от {conn.peer}: {e}")
                break
            try:
                await self.handler(conn, msg_type, payload)
            except Exception as e:
                log.exception(f"Ошибка в handler: {e}")
        await conn.close()
        log.info(f"Соединение с {conn.peer} закрыто")

    async def connect(self, host: str, port: int) -> Connection:
        reader, writer = await asyncio.open_connection(host, port)
        peer = writer.get_extra_info("peername")
        conn = Connection(reader, writer, peer)
        log.info(f"Подключился к {host}:{port}")
        asyncio.create_task(self._serve(conn))
        return conn

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()