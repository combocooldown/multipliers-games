import discord
from datetime import datetime
from typing import Dict, List, Any

class EmbedHelper:
    def __init__(self):
        self.colors = {
            'success': 0x00ff00,
            'error': 0xff0000,
            'info': 0x0099ff,
            'warning': 0xffaa00,
            'gold': 0xffd700,
            'purple': 0x9932cc,
            'casino': 0xff6b35
        }
    
    def create_balance_embed(self, user: discord.User, balance: int) -> discord.Embed:
        """Create balance display embed."""
        embed = discord.Embed(
            title="💰 Your Balance",
            color=self.colors['info']
        )
        
        embed.add_field(
            name="Current Balance",
            value=f"**{balance:,}** coins",
            inline=False
        )
        
        embed.set_author(
            name=user.display_name,
            icon_url=user.display_avatar.url
        )
        
        embed.set_footer(text="Use /daily to claim your daily bonus!")
        embed.timestamp = datetime.now()
        
        return embed
    
    def create_daily_embed(self, user: discord.User, bonus_amount: int) -> discord.Embed:
        """Create daily bonus claim embed."""
        embed = discord.Embed(
            title="🎁 Daily Bonus Claimed!",
            description=f"You received **{bonus_amount:,}** coins!",
            color=self.colors['success']
        )
        
        embed.set_author(
            name=user.display_name,
            icon_url=user.display_avatar.url
        )
        
        embed.set_footer(text="Come back tomorrow for another bonus!")
        embed.timestamp = datetime.now()
        
        return embed
    
    def create_slots_embed(self, user: discord.User, result: Dict[str, Any]) -> discord.Embed:
        """Create slots game result embed."""
        if result['is_win']:
            color = self.colors['success']
            title = f"🎰 {result['win_type']}"
        else:
            color = self.colors['error']
            title = "🎰 Slot Machine"
        
        embed = discord.Embed(title=title, color=color)
        
        # Create reel display
        reels_display = " | ".join(result['reels'])
        embed.add_field(
            name="🎲 Reels",
            value=f"**{reels_display}**",
            inline=False
        )
        
        embed.add_field(name="💰 Bet", value=f"{result['bet']:,} coins", inline=True)
        
        if result['is_win']:
            embed.add_field(
                name="🎊 Payout", 
                value=f"{result['payout']:,} coins", 
                inline=True
            )
            embed.add_field(
                name="📈 Net Gain", 
                value=f"+{result['net_gain']:,} coins", 
                inline=True
            )
            embed.add_field(
                name="⚡ Multiplier", 
                value=f"{result['multiplier']:.1f}x", 
                inline=True
            )
        else:
            embed.add_field(
                name="📉 Loss", 
                value=f"-{result['bet']:,} coins", 
                inline=True
            )
        
        embed.set_author(
            name=user.display_name,
            icon_url=user.display_avatar.url
        )
        
        embed.timestamp = datetime.now()
        
        return embed
    
    def create_roulette_embed(self, user: discord.User, result: Dict[str, Any]) -> discord.Embed:
        """Create roulette game result embed."""
        if result['is_win']:
            color = self.colors['success']
            title = "🎡 Roulette - Winner!"
        else:
            color = self.colors['error']
            title = "🎡 Roulette"
        
        embed = discord.Embed(title=title, color=color)
        
        # Format winning number with color
        number_display = f"**{result['winning_number']}**"
        if result['winning_color'] == 'red':
            number_display = f"🔴 {number_display}"
        elif result['winning_color'] == 'black':
            number_display = f"⚫ {number_display}"
        else:  # green (0)
            number_display = f"🟢 {number_display}"
        
        embed.add_field(
            name="🎲 Winning Number",
            value=number_display,
            inline=False
        )
        
        embed.add_field(
            name="🎯 Your Bet",
            value=f"{result['bet_choice']} ({result['bet']:,} coins)",
            inline=True
        )
        
        if result['is_win']:
            embed.add_field(
                name="🎊 Payout",
                value=f"{result['payout']:,} coins",
                inline=True
            )
            embed.add_field(
                name="📈 Net Gain",
                value=f"+{result['net_gain']:,} coins",
                inline=True
            )
            embed.add_field(
                name="⚡ Multiplier",
                value=f"{result['multiplier']}:1",
                inline=True
            )
        else:
            embed.add_field(
                name="📉 Loss",
                value=f"-{result['bet']:,} coins",
                inline=True
            )
        
        embed.set_author(
            name=user.display_name,
            icon_url=user.display_avatar.url
        )
        
        embed.timestamp = datetime.now()
        
        return embed
    
    def create_blackjack_embed(self, user: discord.User, result: Dict[str, Any]) -> discord.Embed:
        """Create blackjack game result embed."""
        if result['game_state'] == 'playing':
            color = self.colors['info']
            title = "🃏 Blackjack - Your Turn"
        elif result.get('result') in ['player_blackjack', 'player_wins', 'dealer_bust']:
            color = self.colors['success']
            title = "🃏 Blackjack - You Win!"
        elif result.get('result') == 'push':
            color = self.colors['warning']
            title = "🃏 Blackjack - Push"
        else:
            color = self.colors['error']
            title = "🃏 Blackjack - Dealer Wins"
        
        embed = discord.Embed(title=title, color=color)
        
        # Player hand
        embed.add_field(
            name=f"👤 Your Hand ({result['player_value']})",
            value=result['player_hand'],
            inline=False
        )
        
        # Dealer hand
        dealer_info = f"🤖 Dealer Hand"
        if result['dealer_value'] != '?':
            dealer_info += f" ({result['dealer_value']})"
        
        embed.add_field(
            name=dealer_info,
            value=result['dealer_hand'],
            inline=False
        )
        
        embed.add_field(name="💰 Bet", value=f"{result['bet']:,} coins", inline=True)
        
        # Add result information if game is finished
        if result['game_state'] == 'finished' and 'message' in result:
            embed.add_field(
                name="🎲 Result",
                value=result['message'],
                inline=False
            )
            
            if 'payout' in result:
                embed.add_field(
                    name="💰 Payout",
                    value=f"{result['payout']:,} coins",
                    inline=True
                )
                embed.add_field(
                    name="📈 Net Gain",
                    value=f"{result['net_gain']:+,} coins",
                    inline=True
                )
        else:
            embed.add_field(
                name="🎮 Actions",
                value="Use the buttons below to **Hit** or **Stand**",
                inline=False
            )
        
        embed.set_author(
            name=user.display_name,
            icon_url=user.display_avatar.url
        )
        
        embed.timestamp = datetime.now()
        
        return embed
    
    def create_leaderboard_embed(self, bot, top_users: List[Dict[str, Any]]) -> discord.Embed:
        """Create leaderboard embed."""
        embed = discord.Embed(
            title="🏆 Casino Leaderboard",
            description="Top players by balance",
            color=self.colors['gold']
        )
        
        if not top_users:
            embed.add_field(
                name="No Data",
                value="No players found!",
                inline=False
            )
            return embed
        
        # Create leaderboard text
        leaderboard_text = ""
        medals = ["🥇", "🥈", "🥉"]
        
        for i, user_data in enumerate(top_users[:10]):
            try:
                user = bot.get_user(user_data['user_id'])
                username = user.display_name if user else f"User#{user_data['user_id']}"
            except:
                username = f"User#{user_data['user_id']}"
            
            medal = medals[i] if i < 3 else f"{i+1}."
            balance = user_data['balance']
            
            leaderboard_text += f"{medal} **{username}** - {balance:,} coins\n"
        
        embed.add_field(
            name="💰 Top Players",
            value=leaderboard_text,
            inline=False
        )
        
        embed.set_footer(text="Play games to climb the leaderboard!")
        embed.timestamp = datetime.now()
        
        return embed
    
    def create_stats_embed(self, user: discord.User, user_data: Dict[str, Any]) -> discord.Embed:
        """Create user statistics embed."""
        embed = discord.Embed(
            title="📊 Your Casino Statistics",
            color=self.colors['purple']
        )
        
        stats = user_data['stats']
        
        # Overall stats
        total_games = stats['slots_played'] + stats['roulette_played'] + stats['blackjack_played']
        total_wins = stats['slots_won'] + stats['roulette_won'] + stats['blackjack_won']
        win_rate = (total_wins / total_games * 100) if total_games > 0 else 0
        
        embed.add_field(
            name="🎮 Overall",
            value=f"Games: {total_games}\nWins: {total_wins}\nWin Rate: {win_rate:.1f}%",
            inline=True
        )
        
        # Financial stats
        net_profit = stats['total_winnings'] - stats['total_losses']
        embed.add_field(
            name="💰 Financial",
            value=f"Balance: {user_data['balance']:,}\nWinnings: {stats['total_winnings']:,}\nLosses: {stats['total_losses']:,}\nNet: {net_profit:+,}",
            inline=True
        )
        
        # Records
        embed.add_field(
            name="🏆 Records",
            value=f"Biggest Win: {stats['biggest_win']:,}\nBiggest Loss: {stats['biggest_loss']:,}\nBest Streak: {stats['best_streak']}",
            inline=True
        )
        
        # Game-specific stats
        if stats['slots_played'] > 0:
            slots_wr = (stats['slots_won'] / stats['slots_played'] * 100)
            embed.add_field(
                name="🎰 Slots",
                value=f"Played: {stats['slots_played']}\nWon: {stats['slots_won']}\nWin Rate: {slots_wr:.1f}%",
                inline=True
            )
        
        if stats['roulette_played'] > 0:
            roulette_wr = (stats['roulette_won'] / stats['roulette_played'] * 100)
            embed.add_field(
                name="🎡 Roulette",
                value=f"Played: {stats['roulette_played']}\nWon: {stats['roulette_won']}\nWin Rate: {roulette_wr:.1f}%",
                inline=True
            )
        
        if stats['blackjack_played'] > 0:
            blackjack_wr = (stats['blackjack_won'] / stats['blackjack_played'] * 100)
            embed.add_field(
                name="🃏 Blackjack",
                value=f"Played: {stats['blackjack_played']}\nWon: {stats['blackjack_won']}\nWin Rate: {blackjack_wr:.1f}%",
                inline=True
            )
        
        embed.set_author(
            name=user.display_name,
            icon_url=user.display_avatar.url
        )
        
        embed.timestamp = datetime.now()
        
        return embed
    
    def create_help_embed(self) -> discord.Embed:
        """Create help information embed."""
        embed = discord.Embed(
            title="🎰 Casino Bot Help",
            description="Welcome to the Discord Casino! Here are all available commands:",
            color=self.colors['casino']
        )
        
        # Commands
        embed.add_field(
            name="💰 Economy Commands",
            value="`/balance` - Check your current balance\n`/daily` - Claim daily bonus (1,000 coins)\n`/leaderboard` - View top players",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Game Commands",
            value="`/slots <bet>` - Play slot machine\n`/roulette <bet> <choice>` - Play roulette\n`/blackjack <bet>` - Play blackjack",
            inline=False
        )
        
        embed.add_field(
            name="📊 Information Commands",
            value="`/stats` - View your statistics\n`/help` - Show this help message",
            inline=False
        )
        
        # Game rules
        embed.add_field(
            name="🎰 Slots Rules",
            value="Match symbols to win! Special combinations:\n🎊 Triple 7s: 250x\n💎 Triple Diamonds: 120x\n🔔 Triple Bells: 48x\n🍀 Any Two 7s: 10x",
            inline=True
        )
        
        embed.add_field(
            name="🎡 Roulette Bets",
            value="**Numbers:** 0-36 (35:1)\n**Colors:** red/black (1:1)\n**Even/Odd:** even/odd (1:1)\n**Dozens:** 1st12/2nd12/3rd12 (2:1)",
            inline=True
        )
        
        embed.add_field(
            name="🃏 Blackjack",
            value="Get closer to 21 than dealer!\n• Blackjack pays 3:2\n• Dealer hits soft 17\n• Use Hit/Stand buttons",
            inline=True
        )
        
        # Betting limits
        embed.add_field(
            name="💸 Betting Limits",
            value="**Minimum Bet:** 10 coins\n**Maximum Bet:** 10,000 coins\n**Starting Balance:** 10,000 coins",
            inline=False
        )
        
        embed.set_footer(text="Good luck and gamble responsibly! 🍀")
        embed.timestamp = datetime.now()
        
        return embed
