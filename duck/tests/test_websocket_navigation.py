"""
Regression tests for lively websocket navigation ordering.
"""

import asyncio
import unittest
from types import SimpleNamespace

from duck.html.components.core.websocket import EventHandler


class TestLivelyWebSocketNavigation(unittest.IsolatedAsyncioTestCase):
    async def test_navigation_waits_for_pending_session_save(self):
        loop = asyncio.get_running_loop()
        pending_save = loop.create_future()
        sent_payloads = []

        async def send_data(payload):
            sent_payloads.append(payload)

        ws_view = SimpleNamespace(
            pending_session_save=pending_save,
            send_data=send_data,
        )
        handler = EventHandler(ws_view)

        navigation_task = asyncio.create_task(
            handler.handle_navigation([None, None, "/demo", {}])
        )

        await asyncio.sleep(0)

        self.assertFalse(navigation_task.done())
        self.assertEqual(sent_payloads, [])

        pending_save.set_result(None)
        await navigation_task

        self.assertGreaterEqual(len(sent_payloads), 1)
