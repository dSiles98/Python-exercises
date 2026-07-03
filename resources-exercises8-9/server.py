"""
Servidor de eco con generadores y async/await (ejercicios 8.5b y 8.6).
"""

from __future__ import annotations

from collections import deque
from select import select
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, socket
from types import coroutine
from typing import Any, Callable, Deque, Generator, Tuple

tasks: Deque[Generator[Any, None, Any]] = deque()
recv_wait: dict[Any, Generator[Any, None, Any]] = {}
send_wait: dict[Any, Generator[Any, None, Any]] = {}


def run() -> None:
    while any([tasks, recv_wait, send_wait]):
        while not tasks:
            readable_sockets, writable_sockets, _ = select(recv_wait, send_wait, [])
            for ready_socket in readable_sockets:
                tasks.append(recv_wait.pop(ready_socket))
            for ready_socket in writable_sockets:
                tasks.append(send_wait.pop(ready_socket))

        current_task = tasks.popleft()
        try:
            wait_reason, wait_resource = current_task.send(None)
            if wait_reason == "recv":
                recv_wait[wait_resource] = current_task
            elif wait_reason == "send":
                send_wait[wait_resource] = current_task
            else:
                raise RuntimeError(f"Unknown reason {wait_reason!r}")
        except StopIteration:
            print("Task done")


class GenSocket:
    """Wrapper de socket que delega operaciones de E/S con yield from (ej. 8.6)."""

    def __init__(self, wrapped_socket: Any) -> None:
        self.sock = wrapped_socket

    @coroutine
    def accept(self) -> Generator[Any, Any, Tuple[GenSocket, tuple[Any, ...]]]:
        yield "recv", self.sock
        client_socket, client_address = self.sock.accept()
        return GenSocket(client_socket), client_address

    @coroutine
    def recv(self, max_bytes: int) -> Generator[Any, Any, bytes]:
        yield "recv", self.sock
        return self.sock.recv(max_bytes)

    @coroutine
    def send(self, data: bytes) -> Generator[Any, Any, int]:
        yield "send", self.sock
        return self.sock.send(data)

    def __getattr__(self, attribute_name: str) -> Any:
        return getattr(self.sock, attribute_name)


async def tcp_server(
    server_address: tuple[str, int],
    connection_handler: Callable[[GenSocket, tuple[Any, ...]], Any],
) -> None:
    server_socket = GenSocket(socket(AF_INET, SOCK_STREAM))
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind(server_address)
    server_socket.listen(5)
    while True:
        client_socket, client_address = await server_socket.accept()
        tasks.append(connection_handler(client_socket, client_address))


async def echo_handler(client_socket: GenSocket, client_address: tuple[Any, ...]) -> None:
    print("Connection from", client_address)
    while True:
        received_data = await client_socket.recv(1000)
        if not received_data:
            break
        await client_socket.send(b"GOT:" + received_data)
    print("Connection closed")


if __name__ == "__main__":
    tasks.append(tcp_server(("", 25000), echo_handler))
    run()
