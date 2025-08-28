import asyncio
from asyncio import AbstractEventLoop
from loguru import logger

from src.bots.bot import TradingBot


class BotExecutor:
    def __init__(self, bot: TradingBot):
        self.bot = bot
        self.event_loop = asyncio.new_event_loop()
        self.event_loop.set_exception_handler(self.handle_exception)
        asyncio.set_event_loop(self.event_loop)

    def handle_exception(self, loop: AbstractEventLoop, context: dict) -> None:
        logger.warning(f"Event loop exception: {context.get('exception')}")
        if context.get("message") == "Uncaught exception":
            self.stop()

    def start(self):
        try:
            logger.info("Starting bot...")
            self.event_loop.create_task(self.bot.run())
            self.event_loop.run_forever()
        except (KeyboardInterrupt, SystemExit):
            logger.error("Bot interrupted")
        except Exception as e:
            logger.error(f"General error: {e}")
        finally:
            self.stop()

    def stop(self):
        logger.info("Stopping bot...")
        for task in asyncio.all_tasks(self.event_loop):
            task.cancel()