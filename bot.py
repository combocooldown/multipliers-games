import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from games.slots import SlotsGame
from games.roulette import RouletteGame
from games.blackjack import BlackjackGame
from utils.database import Database
from utils.embeds import EmbedHelper
from utils.rate_limiter import RateLimiter

class CasinoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        # Initialize components
        self.db = Database()
        self.embed_helper = EmbedHelper()
        self.rate_limiter = RateLimiter()
        
        # Initialize games
        self.slots_game = SlotsGame(self.db)
        self.roulette_game = RouletteGame(self.db)
        self.blackjack_game = BlackjackGame(self.db)
        
    async def setup_hook(self):
        """Called when the bot is starting up."""
        # Register slash commands
        self.tree.add_command(balance_command)
        self.tree.add_command(daily_command)
        self.tree.add_command(slots_command)
        self.tree.add_command(roulette_command)
        self.tree.add_command(blackjack_command)
        self.tree.add_command(leaderboard_command)
        self.tree.add_command(stats_command)
        self.tree.add_command(help_command)
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when the bot is ready."""
        print(f'{self.user} has connected to Discord!')
        print(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Game(name="🎰 Casino Games | Use /help")
        )

# Create bot instance
bot = CasinoBot()

@app_commands.command(name="balance", description="Check your current balance")
async def balance_command(interaction: discord.Interaction):
    """Check user's current balance."""
    if not bot.rate_limiter.check_rate_limit(interaction.user.id, "balance"):
        await interaction.response.send_message(
            "⏰ Please wait before checking your balance again!", ephemeral=True
        )
        return
    
    user_data = bot.db.get_user(interaction.user.id)
    embed = bot.embed_helper.create_balance_embed(interaction.user, user_data['balance'])
    await interaction.response.send_message(embed=embed)

@app_commands.command(name="daily", description="Claim your daily bonus")
async def daily_command(interaction: discord.Interaction):
    """Claim daily bonus."""
    if not bot.rate_limiter.check_rate_limit(interaction.user.id, "daily"):
        await interaction.response.send_message(
            "⏰ You've already claimed your daily bonus today!", ephemeral=True
        )
        return
    
    bonus_amount = 1000
    bot.db.add_balance(interaction.user.id, bonus_amount)
    
    embed = bot.embed_helper.create_daily_embed(interaction.user, bonus_amount)
    await interaction.response.send_message(embed=embed)

@app_commands.command(name="slots", description="Play the slot machine")
async def slots_command(interaction: discord.Interaction, bet: int = 100):
    """Play slots game."""
    if not bot.rate_limiter.check_rate_limit(interaction.user.id, "game"):
        await interaction.response.send_message(
            "⏰ Please wait before playing again!", ephemeral=True
        )
        return
    
    if bet < 10:
        await interaction.response.send_message(
            "❌ Minimum bet is 10 coins!", ephemeral=True
        )
        return
    
    if bet > 10000:
        await interaction.response.send_message(
            "❌ Maximum bet is 10,000 coins!", ephemeral=True
        )
        return
    
    user_data = bot.db.get_user(interaction.user.id)
    if user_data['balance'] < bet:
        await interaction.response.send_message(
            f"❌ Insufficient balance! You have {user_data['balance']} coins.", 
            ephemeral=True
        )
        return
    
    result = await bot.slots_game.play(interaction.user.id, bet)
    embed = bot.embed_helper.create_slots_embed(interaction.user, result)
    await interaction.response.send_message(embed=embed)

@app_commands.command(name="roulette", description="Play roulette")
async def roulette_command(interaction: discord.Interaction, bet: int, choice: str):
    """Play roulette game."""
    if not bot.rate_limiter.check_rate_limit(interaction.user.id, "game"):
        await interaction.response.send_message(
            "⏰ Please wait before playing again!", ephemeral=True
        )
        return
    
    if bet < 10:
        await interaction.response.send_message(
            "❌ Minimum bet is 10 coins!", ephemeral=True
        )
        return
    
    if bet > 10000:
        await interaction.response.send_message(
            "❌ Maximum bet is 10,000 coins!", ephemeral=True
        )
        return
    
    user_data = bot.db.get_user(interaction.user.id)
    if user_data['balance'] < bet:
        await interaction.response.send_message(
            f"❌ Insufficient balance! You have {user_data['balance']} coins.", 
            ephemeral=True
        )
        return
    
    result = await bot.roulette_game.play(interaction.user.id, bet, choice)
    if result['error']:
        await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)
        return
    
    embed = bot.embed_helper.create_roulette_embed(interaction.user, result)
    await interaction.response.send_message(embed=embed)

@app_commands.command(name="blackjack", description="Play blackjack")
async def blackjack_command(interaction: discord.Interaction, bet: int = 100):
    """Play blackjack game."""
    if not bot.rate_limiter.check_rate_limit(interaction.user.id, "game"):
        await interaction.response.send_message(
            "⏰ Please wait before playing again!", ephemeral=True
        )
        return
    
    if bet < 10:
        await interaction.response.send_message(
            "❌ Minimum bet is 10 coins!", ephemeral=True
        )
        return
    
    if bet > 10000:
        await interaction.response.send_message(
            "❌ Maximum bet is 10,000 coins!", ephemeral=True
        )
        return
    
    user_data = bot.db.get_user(interaction.user.id)
    if user_data['balance'] < bet:
        await interaction.response.send_message(
            f"❌ Insufficient balance! You have {user_data['balance']} coins.", 
            ephemeral=True
        )
        return
    
    result = await bot.blackjack_game.play(interaction.user.id, bet)
    embed = bot.embed_helper.create_blackjack_embed(interaction.user, result)
    
    if result['game_state'] == 'playing':
        view = BlackjackView(bot.blackjack_game, interaction.user.id, result['game_id'])
        await interaction.response.send_message(embed=embed, view=view)
    else:
        await interaction.response.send_message(embed=embed)

@app_commands.command(name="leaderboard", description="View the top players")
async def leaderboard_command(interaction: discord.Interaction):
    """Show leaderboard."""
    if not bot.rate_limiter.check_rate_limit(interaction.user.id, "leaderboard"):
        await interaction.response.send_message(
            "⏰ Please wait before checking the leaderboard again!", ephemeral=True
        )
        return
    
    top_users = bot.db.get_leaderboard()
    embed = bot.embed_helper.create_leaderboard_embed(bot, top_users)
    await interaction.response.send_message(embed=embed)

@app_commands.command(name="stats", description="View your gambling statistics")
async def stats_command(interaction: discord.Interaction):
    """Show user statistics."""
    user_data = bot.db.get_user(interaction.user.id)
    embed = bot.embed_helper.create_stats_embed(interaction.user, user_data)
    await interaction.response.send_message(embed=embed)

@app_commands.command(name="help", description="Show casino help and rules")
async def help_command(interaction: discord.Interaction):
    """Show help information."""
    embed = bot.embed_helper.create_help_embed()
    await interaction.response.send_message(embed=embed)

class BlackjackView(discord.ui.View):
    def __init__(self, blackjack_game, user_id, game_id):
        super().__init__(timeout=300)
        self.blackjack_game = blackjack_game
        self.user_id = user_id
        self.game_id = game_id
    
    @discord.ui.button(label='Hit', style=discord.ButtonStyle.primary, emoji='🃏')
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ This is not your game!", ephemeral=True
            )
            return
        
        result = await self.blackjack_game.hit(self.game_id)
        embed = bot.embed_helper.create_blackjack_embed(interaction.user, result)
        
        if result['game_state'] != 'playing':
            self.clear_items()
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label='Stand', style=discord.ButtonStyle.secondary, emoji='✋')
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ This is not your game!", ephemeral=True
            )
            return
        
        result = await self.blackjack_game.stand(self.game_id)
        embed = bot.embed_helper.create_blackjack_embed(interaction.user, result)
        
        self.clear_items()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def on_timeout(self):
        self.clear_items()

# Export the bot instance
def get_bot():
    return bot

# For running directly
if __name__ == "__main__":
    import asyncio
    
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("ERROR: DISCORD_BOT_TOKEN environment variable is required!")
    else:
        asyncio.run(bot.start(token))
