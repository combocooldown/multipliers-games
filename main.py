import asyncio
import os
from bot import CasinoBot

async def main():
    """Main entry point for the Discord casino bot."""
    # Get bot token from environment variable
    token = os.getenv("DISCORD_BOT_TOKEN")
    
    if not token:
        print("ERROR: DISCORD_BOT_TOKEN environment variable is required!")
        print("Please set your Discord bot token in the environment variables.")
        return
    
    # Create and run the bot
    bot = CasinoBot()
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        print("\nBot shutting down...")
        await bot.close()
    except Exception as e:
        print(f"An error occurred: {e}")
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
