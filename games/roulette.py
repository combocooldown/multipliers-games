import random
from typing import Dict, List, Any

class RouletteGame:
    def __init__(self, database):
        self.db = database
        
        # Roulette wheel (European style - single zero)
        self.numbers = list(range(0, 37))  # 0-36
        
        # Color mappings
        self.red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
        self.black_numbers = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}
        
        # Define betting options and their payouts
        self.bet_types = {
            # Single number bets
            'straight': {'payout': 35, 'description': 'Single number (0-36)'},
            
            # Color bets
            'red': {'payout': 1, 'description': 'Red numbers'},
            'black': {'payout': 1, 'description': 'Black numbers'},
            
            # Even/Odd bets
            'even': {'payout': 1, 'description': 'Even numbers (2,4,6...)'},
            'odd': {'payout': 1, 'description': 'Odd numbers (1,3,5...)'},
            
            # High/Low bets
            'high': {'payout': 1, 'description': 'High numbers (19-36)'},
            'low': {'payout': 1, 'description': 'Low numbers (1-18)'},
            
            # Dozen bets
            '1st12': {'payout': 2, 'description': 'First dozen (1-12)'},
            '2nd12': {'payout': 2, 'description': 'Second dozen (13-24)'},
            '3rd12': {'payout': 2, 'description': 'Third dozen (25-36)'},
            
            # Column bets
            'col1': {'payout': 2, 'description': 'First column'},
            'col2': {'payout': 2, 'description': 'Second column'},
            'col3': {'payout': 2, 'description': 'Third column'},
        }
    
    def spin_wheel(self) -> int:
        """Spin the roulette wheel and return the winning number."""
        return random.choice(self.numbers)
    
    def get_number_color(self, number: int) -> str:
        """Get the color of a number."""
        if number == 0:
            return 'green'
        elif number in self.red_numbers:
            return 'red'
        else:
            return 'black'
    
    def check_win(self, winning_number: int, bet_choice: str) -> bool:
        """Check if a bet wins based on the winning number."""
        bet_choice = bet_choice.lower()
        
        # Single number bet
        if bet_choice.isdigit():
            return int(bet_choice) == winning_number
        
        # Special case for zero
        if winning_number == 0:
            return bet_choice == '0'
        
        # Color bets
        if bet_choice == 'red':
            return winning_number in self.red_numbers
        elif bet_choice == 'black':
            return winning_number in self.black_numbers
        
        # Even/Odd bets
        elif bet_choice == 'even':
            return winning_number % 2 == 0
        elif bet_choice == 'odd':
            return winning_number % 2 == 1
        
        # High/Low bets
        elif bet_choice == 'high':
            return 19 <= winning_number <= 36
        elif bet_choice == 'low':
            return 1 <= winning_number <= 18
        
        # Dozen bets
        elif bet_choice == '1st12':
            return 1 <= winning_number <= 12
        elif bet_choice == '2nd12':
            return 13 <= winning_number <= 24
        elif bet_choice == '3rd12':
            return 25 <= winning_number <= 36
        
        # Column bets
        elif bet_choice == 'col1':
            return winning_number % 3 == 1 and winning_number != 0
        elif bet_choice == 'col2':
            return winning_number % 3 == 2 and winning_number != 0
        elif bet_choice == 'col3':
            return winning_number % 3 == 0 and winning_number != 0
        
        return False
    
    def get_payout_multiplier(self, bet_choice: str) -> int:
        """Get the payout multiplier for a bet type."""
        bet_choice = bet_choice.lower()
        
        # Single number bet
        if bet_choice.isdigit() or bet_choice == '0':
            return self.bet_types['straight']['payout']
        
        # Find the bet type
        for bet_type, data in self.bet_types.items():
            if bet_choice == bet_type:
                return data['payout']
        
        return 0
    
    def validate_bet_choice(self, bet_choice: str) -> Dict[str, Any]:
        """Validate a bet choice."""
        bet_choice = bet_choice.lower()
        
        # Check if it's a valid number
        if bet_choice.isdigit():
            number = int(bet_choice)
            if 0 <= number <= 36:
                return {'valid': True, 'type': 'straight', 'choice': str(number)}
        
        # Check if it's a valid bet type
        if bet_choice in self.bet_types:
            return {'valid': True, 'type': bet_choice, 'choice': bet_choice}
        
        return {'valid': False, 'error': 'Invalid bet choice'}
    
    async def play(self, user_id: int, bet: int, bet_choice: str) -> Dict[str, Any]:
        """Play a roulette game."""
        # Validate bet choice
        validation = self.validate_bet_choice(bet_choice)
        if not validation['valid']:
            return {
                'error': f"Invalid bet choice '{bet_choice}'. Valid options: numbers (0-36), red, black, even, odd, high, low, 1st12, 2nd12, 3rd12, col1, col2, col3",
                'game_type': 'roulette'
            }
        
        # Deduct bet from user balance
        self.db.subtract_balance(user_id, bet)
        
        # Spin the wheel
        winning_number = self.spin_wheel()
        winning_color = self.get_number_color(winning_number)
        
        # Check if bet wins
        is_win = self.check_win(winning_number, bet_choice)
        
        # Calculate payout
        payout = 0
        multiplier = 0
        if is_win:
            multiplier = self.get_payout_multiplier(bet_choice)
            payout = bet * (multiplier + 1)  # Include original bet
            self.db.add_balance(user_id, payout)
        
        net_gain = payout - bet
        
        # Update statistics
        self.db.update_stats(user_id, 'roulette_played', 1)
        if is_win:
            self.db.update_stats(user_id, 'roulette_won', 1)
            self.db.update_stats(user_id, 'total_winnings', net_gain)
        else:
            self.db.update_stats(user_id, 'total_losses', bet)
        
        return {
            'winning_number': winning_number,
            'winning_color': winning_color,
            'bet_choice': bet_choice,
            'bet': bet,
            'is_win': is_win,
            'multiplier': multiplier,
            'payout': payout,
            'net_gain': net_gain,
            'game_type': 'roulette',
            'error': None
        }
    
    def get_betting_help(self) -> str:
        """Get help information about betting options."""
        help_text = "🎡 **Roulette Betting Options:**\n\n"
        
        help_text += "**Single Numbers:** 0-36 (35:1 payout)\n"
        help_text += "**Colors:** red, black (1:1 payout)\n"
        help_text += "**Even/Odd:** even, odd (1:1 payout)\n"
        help_text += "**High/Low:** high (19-36), low (1-18) (1:1 payout)\n"
        help_text += "**Dozens:** 1st12 (1-12), 2nd12 (13-24), 3rd12 (25-36) (2:1 payout)\n"
        help_text += "**Columns:** col1, col2, col3 (2:1 payout)\n\n"
        
        help_text += "**Examples:**\n"
        help_text += "`/roulette 100 17` - Bet 100 on number 17\n"
        help_text += "`/roulette 200 red` - Bet 200 on red\n"
        help_text += "`/roulette 150 1st12` - Bet 150 on first dozen\n"
        
        return help_text
