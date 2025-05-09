import asyncio
from typing import Callable

import httpx


async def process_streaming_response(
    url: str,
    headers: dict,
    on_chunk: Callable[[str], None],
    should_terminate: Callable[[], bool],
    method: str = "GET",
    chunk_timeout: float = 2.0,
    require_consecutive_termination: bool = True,
) -> None:
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(method, url, headers=headers) as response:
            stream = response.aiter_bytes()
            next_chunk = None
            exit_check_streak = 0

            while True:
                if next_chunk is None:
                    next_chunk = asyncio.create_task(anext(stream, None))
                timeout = asyncio.create_task(asyncio.sleep(chunk_timeout))

                done, pending = await asyncio.wait([next_chunk, timeout], return_when=asyncio.FIRST_COMPLETED)

                if next_chunk in done:
                    timeout.cancel()
                    chunk = next_chunk.result()
                    next_chunk = None

                    if chunk is None:
                        break

                    on_chunk(chunk.decode("utf-8"))
                    exit_check_streak = 0  # Reset on activity

                elif timeout in done:
                    should_end = should_terminate()

                    if should_end:
                        exit_check_streak += 1
                        if not require_consecutive_termination or exit_check_streak > 1:
                            if next_chunk in pending:
                                next_chunk.cancel()
                            break
                    else:
                        exit_check_streak = 0
