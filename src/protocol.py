import struct
import msgpack

PING = 1
PONG = 2
MESSAGE = 3

HEADER = struct.Struct("!I")

MAX_FRAME_SIZE = 16 * 1024 * 1024


def encode_frame(msg_type: int, payload: dict) -> bytes:
    body = msgpack.packb(payload, use_bin_type=True)
    length = 1 + len(body)
    if length > MAX_FRAME_SIZE:
        raise ValueError("Кадр слишком большой")
    return HEADER.pack(length) + bytes([msg_type]) + body


async def read_frame(reader):
    header = await reader.readexactly(4)
    (length,) = HEADER.unpack(header)
    if length < 1 or length > MAX_FRAME_SIZE:
        raise ValueError(f"Некорректная длина кадра: {length}")

    body = await reader.readexactly(length)
    msg_type = body[0]
    payload = msgpack.unpackb(body[1:], raw=False) if length > 1 else {}
    return msg_type, payload