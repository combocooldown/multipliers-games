import json
import os
from typing import Dict, List, Any
from datetime import datetime, timedelta
import threading

class Database:
    def __init__(self, filename: str = "casino_data.json"):
        self.filename = filename
        self.data = self._load_data()
        self._lock = threading.Lock()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Return default structure if file doesn't exist or is corrupted
        return {
            'users': {},
            'leaderboard': [],
            'global_stats': {
                'total_games': 0,
                'total_bets': 0,
                'total_payouts': 0
            }
        }
    
    def _save_data(self):
        """Save data to JSON file."""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            print(f"Error saving data: {e}")
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user data, creating new user if doesn't exist."""
        with self._lock:
            user_id_str = str(user_id)
            
            if user_id_str not in self.data['users']:
                # Create new user with starting balance
                self.data['users'][user_id_str] = {
                    'balance': 10000,  # Starting balance
                    'total_bet': 0,
                    'total_won': 0,
                    'games_played': 0,
                    'last_daily': None,
                    'stats': {
                        'slots_played': 0,
                        'slots_won': 0,
                        'roulette_played': 0,
                        'roulette_won': 0,
                        'blackjack_played': 0,
                        'blackjack_won': 0,
                        'total_winnings': 0,
                        'total_losses': 0,
                        'biggest_win': 0,
                        'biggest_loss': 0,
                        'current_streak': 0,
                        'best_streak': 0
                    },
                    'created_at': datetime.now().isoformat(),
                    'last_played': datetime.now().isoformat()
                }
                self._save_data()
            else:
                # Update last played timestamp
                self.data['users'][user_id_str]['last_played'] = datetime.now().isoformat()
            
            return self.data['users'][user_id_str].copy()
    
    def add_balance(self, user_id: int, amount: int):
        """Add balance to user account."""
        with self._lock:
            user_data = self.get_user(user_id)
            user_id_str = str(user_id)
            
            self.data['users'][user_id_str]['balance'] += amount
            self._save_data()
    
    def subtract_balance(self, user_id: int, amount: int) -> bool:
        """Subtract balance from user account. Returns True if successful."""
        with self._lock:
            user_data = self.get_user(user_id)
            user_id_str = str(user_id)
            
            if user_data['balance'] >= amount:
                self.data['users'][user_id_str]['balance'] -= amount
                self.data['users'][user_id_str]['total_bet'] += amount
                self._save_data()
                return True
            return False
    
    def update_stats(self, user_id: int, stat_name: str, value: int):
        """Update user statistics."""
        with self._lock:
            user_data = self.get_user(user_id)
            user_id_str = str(user_id)
            
            if stat_name in self.data['users'][user_id_str]['stats']:
                self.data['users'][user_id_str]['stats'][stat_name] += value
                
                # Update biggest win/loss
                if stat_name == 'total_winnings' and value > 0:
                    current_biggest = self.data['users'][user_id_str]['stats']['biggest_win']
                    if value > current_biggest:
                        self.data['users'][user_id_str]['stats']['biggest_win'] = value
                
                if stat_name == 'total_losses' and value > 0:
                    current_biggest = self.data['users'][user_id_str]['stats']['biggest_loss']
                    if value > current_biggest:
                        self.data['users'][user_id_str]['stats']['biggest_loss'] = value
                
                self._save_data()
    
    def can_claim_daily(self, user_id: int) -> bool:
        """Check if user can claim daily bonus."""
        user_data = self.get_user(user_id)
        
        if user_data['last_daily'] is None:
            return True
        
        last_daily = datetime.fromisoformat(user_data['last_daily'])
        now = datetime.now()
        
        # Check if 24 hours have passed
        return (now - last_daily) >= timedelta(hours=24)
    
    def claim_daily(self, user_id: int, amount: int):
        """Claim daily bonus."""
        with self._lock:
            user_id_str = str(user_id)
            self.data['users'][user_id_str]['last_daily'] = datetime.now().isoformat()
            self.add_balance(user_id, amount)
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top users by balance."""
        users = []
        
        for user_id, user_data in self.data['users'].items():
            users.append({
                'user_id': int(user_id),
                'balance': user_data['balance'],
                'total_bet': user_data['total_bet'],
                'total_won': user_data['total_won'],
                'games_played': user_data['games_played']
            })
        
        # Sort by balance (descending)
        users.sort(key=lambda x: x['balance'], reverse=True)
        
        return users[:limit]
    
    def get_user_rank(self, user_id: int) -> int:
        """Get user's rank on leaderboard."""
        leaderboard = self.get_leaderboard(limit=1000)  # Get more entries to find rank
        
        for i, user in enumerate(leaderboard):
            if user['user_id'] == user_id:
                return i + 1
        
        return len(leaderboard) + 1
    
    def update_global_stats(self, stat_name: str, value: int):
        """Update global statistics."""
        with self._lock:
            if stat_name in self.data['global_stats']:
                self.data['global_stats'][stat_name] += value
                self._save_data()
    
    def get_global_stats(self) -> Dict[str, int]:
        """Get global statistics."""
        return self.data['global_stats'].copy()
    
    def backup_data(self) -> str:
        """Create a backup of the current data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"casino_backup_{timestamp}.json"
        
        try:
            with open(backup_filename, 'w') as f:
                json.dump(self.data, f, indent=2)
            return backup_filename
        except IOError as e:
            print(f"Error creating backup: {e}")
            return None
    
    def get_user_count(self) -> int:
        """Get total number of registered users."""
        return len(self.data['users'])
    
    def reset_user_data(self, user_id: int):
        """Reset user data (admin function)."""
        with self._lock:
            user_id_str = str(user_id)
            if user_id_str in self.data['users']:
                del self.data['users'][user_id_str]
                self._save_data()
