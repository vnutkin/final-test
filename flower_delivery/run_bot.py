import asyncio
from bot.apps import BotConfig

# Создаем экземпляр конфигурации бота
bot_app_config = BotConfig("bot", "bot")

async def main():
    await bot_app_config.start_bot()

if __name__ == "__main__":
    asyncio.run(main())