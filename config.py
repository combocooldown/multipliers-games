import os
from typing import Dict, Any

class Config:
    """Configuration settings for the Discord Casino Bot."""
    
    # Bot settings
    BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
    COMMAND_PREFIX = "!"
    
    # Database settings
    DATABASE_FILE = "casino_data.json"
    BACKUP_INTERVAL_HOURS = 24
    
    # Game settings
    STARTING_BALANCE = 10000
    DAILY_BONUS = 1000
    
    # Betting limits
    MIN_BET = 10
    MAX_BET = 10000
    
    # Rate limiting (in seconds)
    RATE_LIMITS = {
        'game': 3,          # Time between games
        'balance': 5,       # Time between balance checks
        'daily': 86400,     # Daily bonus cooldown (24 hours)
        'leaderboard': 10,  # Time between leaderboard views
        'stats': 5          # Time between stats views
    }
    
    # Casino game settings
    SLOTS_CONFIG = {
        'symbols': {
            '🍒': {'value': 2, 'weight': 30},    # Cherry - common
            '🍋': {'value': 3, 'weight': 25},    # Lemon - common
            '🍊': {'value': 4, 'weight': 20},    # Orange - uncommon
            '🍇': {'value': 5, 'weight': 15},    # Grape - uncommon
            '🔔': {'value': 8, 'weight': 7},     # Bell - rare
            '💎': {'value': 15, 'weight': 2},    # Diamond - very rare
            '7️⃣': {'value': 25, 'weight': 1}     # Lucky 7 - ultra rare
        },
        'jackpot_multipliers': {
            '7️⃣': 10,   # 250x for triple 7s
            '💎': 8,    # 120x for triple diamonds
            '🔔': 6,    # 48x for triple bells
            'other': 4  # 4x base value for other triples
        }
    }
    
    BLACKJACK_CONFIG = {
        'blackjack_payout': 2.5,   # 3:2 payout for blackjack
        'dealer_hits_soft_17': True,
        'max_game_time_minutes': 5
    }
    
    ROULETTE_CONFIG = {
        'wheel_type': 'european',  # Single zero (0-36)
        'bet_types': {
            'straight': 35,    # Single number
            'color': 1,        # Red/Black
            'even_odd': 1,     # Even/Odd
            'high_low': 1,     # High (19-36) / Low (1-18)
            'dozen': 2,        # 1st12, 2nd12, 3rd12
            'column': 2        # Column bets
        }
    }
    
    # Discord embed colors (hex values)
    EMBED_COLORS = {
        'success': 0x00ff00,
        'error': 0xff0000,
        'info': 0x0099ff,
        'warning': 0xffaa00,
        'gold': 0xffd700,
        'purple': 0x9932cc,
        'casino': 0xff6b35
    }
    
    # Bot status messages
    STATUS_MESSAGES = [
        "🎰 Casino Games",
        "🎲 Roll the dice!",
        "💰 Win big!",
        "🃏 Blackjack time!",
        "🎡 Spin to win!"
    ]
    
    # Error messages
    ERROR_MESSAGES = {
        'insufficient_funds': "❌ Insufficient balance! You need at least {amount} coins.",
        'bet_too_low': f"❌ Minimum bet is {MIN_BET} coins!",
        'bet_too_high': f"❌ Maximum bet is {MAX_BET:,} coins!",
        'rate_limited': "⏰ Please wait {time} seconds before using this command again!",
        'invalid_bet': "❌ Please enter a valid bet amount!",
        'game_not_found': "❌ Game session not found or expired!",
        'not_your_game': "❌ This is not your game session!",
        'daily_claimed': "⏰ You've already claimed your daily bonus today!",
        'invalid_roulette_bet': "❌ Invalid roulette bet. Use /help for valid options."
    }
    
    # Success messages
    SUCCESS_MESSAGES = {
        'daily_claimed': "🎁 Daily bonus of {amount} coins claimed!",
        'balance_added': "💰 {amount} coins added to your balance!",
        'game_win': "🎉 Congratulations! You won {amount} coins!",
        'new_record': "🏆 New personal record: {amount} coins!"
    }
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration settings and return validation results."""
        issues = []
        warnings = []
        
        # Check bot token
        if not cls.BOT_TOKEN:
            issues.append("DISCORD_BOT_TOKEN environment variable is required")
        
        # Validate betting limits
        if cls.MIN_BET >= cls.MAX_BET:
            issues.append("MIN_BET must be less than MAX_BET")
        
        if cls.MIN_BET <= 0:
            issues.append("MIN_BET must be positive")
        
        if cls.STARTING_BALANCE < cls.MAX_BET:
            warnings.append("STARTING_BALANCE is less than MAX_BET")
        
        # Validate slots symbols
        total_weight = sum(symbol['weight'] for symbol in cls.SLOTS_CONFIG['symbols'].values())
        if total_weight <= 0:
            issues.append("Slots symbols must have positive weights")
        
        # Validate rate limits
        for action, limit in cls.RATE_LIMITS.items():
            if limit < 0:
                issues.append(f"Rate limit for '{action}' must be non-negative")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    @classmethod
    def get_help_text(cls) -> str:
        """Get formatted help text for the bot."""
        return f"""
**🎰 Discord Casino Bot**

**Economy Commands:**
• `/balance` - Check your current balance
• `/daily` - Claim daily bonus ({cls.DAILY_BONUS:,} coins)
• `/leaderboard` - View top players

**Game Commands:**
• `/slots <bet>` - Play slot machine
• `/roulette <bet> <choice>` - Play roulette
• `/blackjack <bet>` - Play blackjack

**Information Commands:**
• `/stats` - View your statistics
• `/help` - Show this help message

**Betting Limits:**
• Minimum bet: {cls.MIN_BET} coins
• Maximum bet: {cls.MAX_BET:,} coins
• Starting balance: {cls.STARTING_BALANCE:,} coins

Good luck and gamble responsibly! 🍀
        """.strip()
