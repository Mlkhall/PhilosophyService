import asyncio
from functools import wraps

import aiohttp
from loguru import logger

from ..models.collector_model import CollectorResponse


def async_backoff(*, start_sleep_time=0.1, factor=1, border_sleep_time=2):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.

    Использует наивный экспоненциальный рост времени повтора
    (factor) до граничного времени ожидания (border_sleep_time).

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time

    Args:
        start_sleep_time:
            начальное время повтора
        factor:
            во сколько раз нужно увеличить время ожидания
        border_sleep_time:
            граничное время ожидания (в секундах)

    Returns:
        :return: результат выполнения функции

    """

    def func_wrapper(method):
        @wraps(method)
        async def inner(*args, **kwargs):
            sleep_time = start_sleep_time

            while True:
                if sleep_time >= border_sleep_time:
                    logger.error("Max retries exceeded!")
                    raise ValueError("start_sleep_time must be less than border_sleep_time")

                try:
                    response = await method(*args, **kwargs)
                except aiohttp.ClientError:
                    logger.warning(f"Waiting for {sleep_time} seconds...")
                    await asyncio.sleep(sleep_time)
                    sleep_time = min(sleep_time * 2**factor, border_sleep_time)
                else:
                    if isinstance(response, CollectorResponse):
                        if "ввести капчу" in response.page_content:
                            logger.warning(f"Kapcha detected! Waiting for {sleep_time} seconds...")
                            await asyncio.sleep(sleep_time)
                            sleep_time = min(sleep_time * 2**factor, border_sleep_time)
                        else:
                            return response
                    else:
                        return response

        return inner

    return func_wrapper
