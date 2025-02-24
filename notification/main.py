import asyncio

from app.api import get_consumer


async def main():
    consumer = get_consumer()

    try:
        await consumer.start()
        await asyncio.Future()  # run forever
    except KeyboardInterrupt:
        await consumer.close()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
