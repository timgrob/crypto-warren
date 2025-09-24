import uvloop
import asyncio
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from src.bots.trading_bot import TradingBot

uvloop.install()
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class BotExecutor:
    def __init__(self, bot: TradingBot):
        self.bot = bot
        self.bot_name = bot.__class__.__name__
        self.scheduler = AsyncIOScheduler({"apscheduler.timezone": "UTC"})

    def run(self):
        asyncio.run(self._run())

    async def _run(self):
        try:
            await self._startup()
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            pass
        except Exception as e:
            logger.error(f"Exception in bot {self.bot_name}: {e}")
        finally:
            await self._shutdown()

    async def _startup(self):
        logger.info(f"Starting bot {self.bot_name}")
        await self.bot.on_start()

        rate = self.bot.config.rate
        is_crontab = not rate.replace(".", "", 1).isdigit()
        trigger = (
            CronTrigger.from_crontab(rate)
            if is_crontab
            else IntervalTrigger(seconds=int(rate))
        )
        self.scheduler.add_job(self.bot.trade, trigger, name="Trade loop")
        self.scheduler.start()
        logger.info(f"Scheduler started for {self.bot_name}")

    async def _shutdown(self):
        logger.info(f"Bot stopping {self.bot_name}")
        await self.bot.on_stop()
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
        logger.info(f"Scheduler stopped for {self.bot_name}")
