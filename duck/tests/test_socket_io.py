"""
Tests for HTTP request framing over Duck sockets.
"""
import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from duck.tests.test_server import set_settings


set_settings({"request_stream_timeout": 1})

from duck.utils.xsocket import xsocket
from duck.utils.xsocket.io import SocketIO


EMPTY_GET_REQUEST = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"


class TestSocketIORequestFraming(unittest.TestCase):
    """
    Verifies that requests without a body delimiter complete at their headers.
    """

    def test_receive_full_request_does_not_wait_for_empty_get_body(self) -> None:
        """
        Returns an HTTP GET request without attempting a second body read.
        """
        socket_wrapper = object.__new__(xsocket)

        with patch.object(SocketIO, "receive", return_value=EMPTY_GET_REQUEST) as receive:
            request = SocketIO.receive_full_request(
                socket_wrapper,
                timeout=1,
                stream_timeout=1,
            )

        self.assertEqual(request, EMPTY_GET_REQUEST)
        receive.assert_called_once_with(socket_wrapper, timeout=1)

    def test_async_receive_full_request_does_not_wait_for_empty_get_body(self) -> None:
        """
        Returns an asynchronous HTTP GET without attempting a second body read.
        """
        async def async_receive_request() -> bytes:
            socket_wrapper = object.__new__(xsocket)

            with patch.object(
                SocketIO,
                "async_receive",
                new_callable=AsyncMock,
                return_value=EMPTY_GET_REQUEST,
            ) as receive:
                request = await SocketIO.async_receive_full_request(
                    socket_wrapper,
                    timeout=1,
                    stream_timeout=1,
                )
                receive.assert_awaited_once_with(socket_wrapper, timeout=1)
                return request

        request = asyncio.run(async_receive_request())

        self.assertEqual(request, EMPTY_GET_REQUEST)
