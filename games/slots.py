import random
import asyncio
from typing import Dict, List, Any

class SlotsGame:
    def __init__(self, database):
        self.db = database
        
        # Slot symbols with their values and probabilities
        self.symbols = {
            '🍒': {'value': 2, 'weight': 30},    # Cherry - common
            '🍋': {'value': 3, 'weight': 25},    # Lemon - common
            '🍊': {'value': 4, 'weight': 20},    # Orange - uncommon
            '🍇': {'value': 5, 'weight': 15},    # Grape - uncommon
            '🔔': {'value': 8, 'weight': 7},     # Bell - rare
            '💎': {'value': 15, 'weight': 2},    # Diamond - very rare
            '7️⃣': {'value': 25, 'weight': 1}     # Lucky 7 - ultra rare
        }
        
        # Create weighted list for random selection
        self.symbol_pool = []
        for symbol, data in self.symbols.items():
            self.symbol_pool.extend([symbol] * data['weight'])
    
    def spin_reels(self) -> List[str]:
        """Spin the slot machine reels."""
        return [random.choice(self.symbol_pool) for _ in range(3)]
    
    def calculate_payout(self, reels: List[str], bet: int) -> Dict[str, Any]:
        """Calculate payout based on reel results."""
        # Count occurrences of each symbol
        symbol_counts = {}
        for symbol in reels:
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        
        # Check for winning combinations
        multiplier = 0
        win_type = ""
        
        # Three of a kind (jackpot)
        if len(symbol_counts) == 1:
            symbol = reels[0]
            base_multiplier = self.symbols[symbol]['value']
            
            # Special jackpot bonuses
            if symbol == '7️⃣':
                multiplier = base_multiplier * 10  # 250x for triple 7s
                win_type = "🎊 MEGA JACKPOT! 🎊"
            elif symbol == '💎':
                multiplier = base_multiplier * 8   # 120x for triple diamonds
                win_type = "💎 DIAMOND JACKPOT! 💎"
            elif symbol == '🔔':
                multiplier = base_multiplier * 6   # 48x for triple bells
                win_type = "🔔 BELL JACKPOT! 🔔"
            else:
                multiplier = base_multiplier * 4   # 4x base value for other triples
                win_type = f"🎰 TRIPLE {symbol}! 🎰"
        
        # Two of a kind
        elif len(symbol_counts) == 2:
            # Find the symbol that appears twice
            for symbol, count in symbol_counts.items():
                if count == 2:
                    multiplier = self.symbols[symbol]['value'] * 0.5
                    win_type = f"🎯 DOUBLE {symbol}! 🎯"
                    break
        
        # Special combination: Any two 7s
        elif symbol_counts.get('7️⃣', 0) >= 2:
            multiplier = 10
            win_type = "🍀 LUCKY SEVENS! 🍀"
        
        # Special combination: Any two diamonds
        elif symbol_counts.get('💎', 0) >= 2:
            multiplier = 8
            win_type = "✨ DIAMOND PAIR! ✨"
        
        # No win
        else:
            multiplier = 0
            win_type = "💸 No Win 💸"
        
        # Calculate final payout
        payout = int(bet * multiplier)
        net_gain = payout - bet
        
        return {
            'reels': reels,
            'multiplier': multiplier,
            'payout': payout,
            'net_gain': net_gain,
            'win_type': win_type,
            'is_win': multiplier > 0
        }
    
    async def play(self, user_id: int, bet: int) -> Dict[str, Any]:
        """Play a slots game."""
        # Deduct bet from user balance
        self.db.subtract_balance(user_id, bet)
        
        # Spin the reels
        reels = self.spin_reels()
        
        # Calculate result
        result = self.calculate_payout(reels, bet)
        
        # Update user balance if they won
        if result['is_win']:
            self.db.add_balance(user_id, result['payout'])
        
        # Update statistics
        self.db.update_stats(user_id, 'slots_played', 1)
        if result['is_win']:
            self.db.update_stats(user_id, 'slots_won', 1)
            self.db.update_stats(user_id, 'total_winnings', result['net_gain'])
        else:
            self.db.update_stats(user_id, 'total_losses', bet)
        
        # Add game metadata
        result['bet'] = bet
        result['game_type'] = 'slots'
        
        return result
    
    def get_symbol_info(self) -> str:
        """Get information about symbols and their values."""
        info = "🎰 **Slot Machine Symbols:**\n\n"
        
        sorted_symbols = sorted(self.symbols.items(), key=lambda x: x[1]['value'], reverse=True)
        
        for symbol, data in sorted_symbols:
            info += f"{symbol} - {data['value']}x multiplier\n"
        
        info += "\n**Special Payouts:**\n"
        info += "🎊 Triple 7s: 250x bet\n"
        info += "💎 Triple Diamonds: 120x bet\n"
        info += "🔔 Triple Bells: 48x bet\n"
        info += "🎰 Other Triples: 4x symbol value\n"
        info += "🎯 Doubles: 0.5x symbol value\n"
        info += "🍀 Any Two 7s: 10x bet\n"
        info += "✨ Any Two Diamonds: 8x bet\n"
        
        return info
