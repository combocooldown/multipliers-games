import random
import asyncio
from typing import Dict, List, Any, Optional
import uuid

class BlackjackGame:
    def __init__(self, database):
        self.db = database
        self.active_games = {}  # Store active game sessions
        
        # Card values
        self.card_values = {
            'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10
        }
        
        # Card suits for display
        self.suits = ['♠️', '♥️', '♦️', '♣️']
        self.ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    def create_deck(self) -> List[Dict[str, str]]:
        """Create a standard 52-card deck."""
        deck = []
        for suit in self.suits:
            for rank in self.ranks:
                deck.append({'rank': rank, 'suit': suit})
        
        random.shuffle(deck)
        return deck
    
    def card_value(self, card: Dict[str, str]) -> int:
        """Get the value of a card."""
        return self.card_values[card['rank']]
    
    def hand_value(self, hand: List[Dict[str, str]]) -> int:
        """Calculate the value of a hand, handling aces properly."""
        value = 0
        aces = 0
        
        for card in hand:
            if card['rank'] == 'A':
                aces += 1
                value += 11
            else:
                value += self.card_value(card)
        
        # Handle aces (convert from 11 to 1 if bust)
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value
    
    def format_hand(self, hand: List[Dict[str, str]], hide_first: bool = False) -> str:
        """Format a hand for display."""
        if hide_first and len(hand) > 0:
            # Show only the second card for dealer's initial hand
            cards = ['🂠'] + [f"{card['rank']}{card['suit']}" for card in hand[1:]]
        else:
            cards = [f"{card['rank']}{card['suit']}" for card in hand]
        
        return ' '.join(cards)
    
    def is_blackjack(self, hand: List[Dict[str, str]]) -> bool:
        """Check if a hand is a natural blackjack."""
        return len(hand) == 2 and self.hand_value(hand) == 21
    
    def should_dealer_hit(self, dealer_hand: List[Dict[str, str]]) -> bool:
        """Determine if dealer should hit (dealer hits on soft 17)."""
        value = self.hand_value(dealer_hand)
        
        if value < 17:
            return True
        elif value == 17:
            # Check for soft 17 (ace counted as 11)
            has_ace_as_11 = False
            temp_value = 0
            for card in dealer_hand:
                if card['rank'] == 'A':
                    temp_value += 11
                    if temp_value <= 17:
                        has_ace_as_11 = True
                else:
                    temp_value += self.card_value(card)
            
            return has_ace_as_11 and temp_value == 17
        
        return False
    
    async def play(self, user_id: int, bet: int) -> Dict[str, Any]:
        """Start a new blackjack game."""
        # Deduct bet from user balance
        self.db.subtract_balance(user_id, bet)
        
        # Create new game
        game_id = str(uuid.uuid4())
        deck = self.create_deck()
        
        # Deal initial cards
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        
        # Check for natural blackjacks
        player_bj = self.is_blackjack(player_hand)
        dealer_bj = self.is_blackjack(dealer_hand)
        
        game_state = {
            'game_id': game_id,
            'user_id': user_id,
            'bet': bet,
            'deck': deck,
            'player_hand': player_hand,
            'dealer_hand': dealer_hand,
            'game_state': 'playing',
            'result': None
        }
        
        # Handle natural blackjacks
        if player_bj and dealer_bj:
            # Push (tie)
            self.db.add_balance(user_id, bet)  # Return bet
            game_state['game_state'] = 'finished'
            game_state['result'] = 'push'
        elif player_bj:
            # Player blackjack wins 3:2
            payout = int(bet * 2.5)
            self.db.add_balance(user_id, payout)
            game_state['game_state'] = 'finished'
            game_state['result'] = 'player_blackjack'
        elif dealer_bj:
            # Dealer blackjack, player loses
            game_state['game_state'] = 'finished'
            game_state['result'] = 'dealer_blackjack'
        
        # Store active game if still playing
        if game_state['game_state'] == 'playing':
            self.active_games[game_id] = game_state
        
        # Update statistics
        self.db.update_stats(user_id, 'blackjack_played', 1)
        
        return self._format_game_result(game_state)
    
    async def hit(self, game_id: str) -> Dict[str, Any]:
        """Player hits (takes another card)."""
        if game_id not in self.active_games:
            return {'error': 'Game not found or already finished'}
        
        game = self.active_games[game_id]
        
        # Deal a card to player
        card = game['deck'].pop()
        game['player_hand'].append(card)
        
        # Check if player busts
        player_value = self.hand_value(game['player_hand'])
        if player_value > 21:
            game['game_state'] = 'finished'
            game['result'] = 'player_bust'
            self._finish_game(game_id)
        
        return self._format_game_result(game)
    
    async def stand(self, game_id: str) -> Dict[str, Any]:
        """Player stands (dealer's turn)."""
        if game_id not in self.active_games:
            return {'error': 'Game not found or already finished'}
        
        game = self.active_games[game_id]
        
        # Dealer's turn
        while self.should_dealer_hit(game['dealer_hand']):
            card = game['deck'].pop()
            game['dealer_hand'].append(card)
        
        # Determine winner
        player_value = self.hand_value(game['player_hand'])
        dealer_value = self.hand_value(game['dealer_hand'])
        
        if dealer_value > 21:
            # Dealer busts, player wins
            payout = game['bet'] * 2
            self.db.add_balance(game['user_id'], payout)
            game['result'] = 'dealer_bust'
        elif player_value > dealer_value:
            # Player wins
            payout = game['bet'] * 2
            self.db.add_balance(game['user_id'], payout)
            game['result'] = 'player_wins'
        elif dealer_value > player_value:
            # Dealer wins
            game['result'] = 'dealer_wins'
        else:
            # Push (tie)
            self.db.add_balance(game['user_id'], game['bet'])  # Return bet
            game['result'] = 'push'
        
        game['game_state'] = 'finished'
        self._finish_game(game_id)
        
        return self._format_game_result(game)
    
    def _finish_game(self, game_id: str):
        """Clean up finished game and update stats."""
        if game_id in self.active_games:
            game = self.active_games[game_id]
            
            # Update statistics
            if game['result'] in ['player_blackjack', 'player_wins', 'dealer_bust']:
                self.db.update_stats(game['user_id'], 'blackjack_won', 1)
                winnings = game['bet'] if game['result'] != 'player_blackjack' else int(game['bet'] * 1.5)
                self.db.update_stats(game['user_id'], 'total_winnings', winnings)
            elif game['result'] in ['dealer_blackjack', 'dealer_wins', 'player_bust']:
                self.db.update_stats(game['user_id'], 'total_losses', game['bet'])
            
            # Remove from active games
            del self.active_games[game_id]
    
    def _format_game_result(self, game: Dict[str, Any]) -> Dict[str, Any]:
        """Format game state for display."""
        player_value = self.hand_value(game['player_hand'])
        dealer_value = self.hand_value(game['dealer_hand'])
        
        # Hide dealer's first card if game is still playing
        hide_dealer_card = game['game_state'] == 'playing'
        
        result = {
            'game_id': game['game_id'],
            'game_state': game['game_state'],
            'bet': game['bet'],
            'player_hand': self.format_hand(game['player_hand']),
            'dealer_hand': self.format_hand(game['dealer_hand'], hide_dealer_card),
            'player_value': player_value,
            'dealer_value': dealer_value if not hide_dealer_card else '?',
            'result': game['result'],
            'game_type': 'blackjack'
        }
        
        # Add win/loss information
        if game['result']:
            if game['result'] == 'player_blackjack':
                result['payout'] = int(game['bet'] * 2.5)
                result['net_gain'] = int(game['bet'] * 1.5)
                result['message'] = "🃏 BLACKJACK! 🃏"
            elif game['result'] in ['player_wins', 'dealer_bust']:
                result['payout'] = game['bet'] * 2
                result['net_gain'] = game['bet']
                result['message'] = "🎉 You Win! 🎉"
            elif game['result'] == 'push':
                result['payout'] = game['bet']
                result['net_gain'] = 0
                result['message'] = "🤝 Push (Tie) 🤝"
            else:
                result['payout'] = 0
                result['net_gain'] = -game['bet']
                result['message'] = "💸 You Lose 💸"
        
        return result
    
    def get_rules(self) -> str:
        """Get blackjack rules and information."""
        rules = "🃏 **Blackjack Rules:**\n\n"
        rules += "• Goal: Get as close to 21 as possible without going over\n"
        rules += "• Face cards (J, Q, K) are worth 10 points\n"
        rules += "• Aces are worth 11 or 1 (whichever is better)\n"
        rules += "• Blackjack (21 with 2 cards) pays 3:2\n"
        rules += "• Dealer hits on soft 17\n"
        rules += "• Player wins ties on blackjack\n\n"
        
        rules += "**Commands:**\n"
        rules += "• Use the Hit button to take another card\n"
        rules += "• Use the Stand button to end your turn\n"
        
        return rules
