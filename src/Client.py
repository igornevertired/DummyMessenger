import asyncio
import aiohttp
import random
import time
from logger import logger

SERVER_URLS = ['http://127.0.0.1:5001/add_message',
               'http://127.0.0.1:5002/add_message']

USERS = ["Alice", "Bob", "Charlie", "David", "Eve",
         "Frank", "Grace", "Heidi", "Ivan", "Judy"]


async def send_message(session):
    """
    Функция отправки запроса на сервер

    """

    user = random.choice(USERS)
    url = random.choice(SERVER_URLS)
    async with session.post(url, params={'name': user, 'text': f"Hello world! {random.randint(10000, 99999)}"}) as resp:
        return await resp.json()


async def main():
    """
    Запуск 50 конкурентных корутин для отправки 5000 сообщений

    """

    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [send_message(session) for _ in range(5000)]
        await asyncio.gather(*tasks)

    total_time = time.time() - start_time
    logger.info(f'Total 5000 requests: {total_time:.2f} seconds')
    logger.info(f'One request: {total_time / 5000:.5f} seconds')
    logger.info(f'RPS: {5000 / total_time:.2f}')


if __name__ == '__main__':
    asyncio.run(main())
