import time
from typing import Dict, Any
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        # Store last action times for each user and action type
        self.user_cooldowns = defaultdict(dict)
        
        # Cooldown periods in seconds
        self.cooldowns = {
            'game': 3,          # 3 seconds between games
            'balance': 5,       # 5 seconds between balance checks
            'daily': 86400,     # 24 hours for daily bonus
            'leaderboard': 10,  # 10 seconds between leaderboard views
            'stats': 5          # 5 seconds between stats views
        }
    
    def check_rate_limit(self, user_id: int, action: str) -> bool:
        """
        Check if user can perform an action based on rate limits.
        Returns True if action is allowed, False if rate limited.
        """
        if action not in self.cooldowns:
            return True  # No limit for unknown actions
        
        current_time = time.time()
        user_id_str = str(user_id)
        
        # Check if user has performed this action before
        if action in self.user_cooldowns[user_id_str]:
            last_action_time = self.user_cooldowns[user_id_str][action]
            time_since_last = current_time - last_action_time
            
            # Check if cooldown period has passed
            if time_since_last < self.cooldowns[action]:
                return False
        
        # Update last action time
        self.user_cooldowns[user_id_str][action] = current_time
        return True
    
    def get_remaining_cooldown(self, user_id: int, action: str) -> float:
        """
        Get remaining cooldown time in seconds.
        Returns 0 if no cooldown is active.
        """
        if action not in self.cooldowns:
            return 0
        
        current_time = time.time()
        user_id_str = str(user_id)
        
        if action in self.user_cooldowns[user_id_str]:
            last_action_time = self.user_cooldowns[user_id_str][action]
            time_since_last = current_time - last_action_time
            remaining = self.cooldowns[action] - time_since_last
            
            return max(0, remaining)
        
        return 0
    
    def reset_user_cooldowns(self, user_id: int):
        """Reset all cooldowns for a specific user (admin function)."""
        user_id_str = str(user_id)
        if user_id_str in self.user_cooldowns:
            del self.user_cooldowns[user_id_str]
    
    def reset_action_cooldown(self, user_id: int, action: str):
        """Reset specific action cooldown for a user (admin function)."""
        user_id_str = str(user_id)
        if user_id_str in self.user_cooldowns and action in self.user_cooldowns[user_id_str]:
            del self.user_cooldowns[user_id_str][action]
    
    def set_custom_cooldown(self, action: str, seconds: int):
        """Set custom cooldown for an action type."""
        self.cooldowns[action] = seconds
    
    def get_cooldown_info(self) -> Dict[str, int]:
        """Get all cooldown periods."""
        return self.cooldowns.copy()
    
    def is_user_rate_limited(self, user_id: int) -> Dict[str, Any]:
        """
        Check which actions are currently rate limited for a user.
        Returns dict with action names and remaining cooldown times.
        """
        rate_limited = {}
        current_time = time.time()
        user_id_str = str(user_id)
        
        if user_id_str not in self.user_cooldowns:
            return rate_limited
        
        for action, cooldown_period in self.cooldowns.items():
            if action in self.user_cooldowns[user_id_str]:
                last_action_time = self.user_cooldowns[user_id_str][action]
                time_since_last = current_time - last_action_time
                remaining = cooldown_period - time_since_last
                
                if remaining > 0:
                    rate_limited[action] = remaining
        
        return rate_limited
    
    def cleanup_old_entries(self, max_age_hours: int = 24):
        """
        Clean up old cooldown entries to prevent memory bloat.
        Removes entries older than max_age_hours.
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        users_to_remove = []
        
        for user_id, user_cooldowns in self.user_cooldowns.items():
            actions_to_remove = []
            
            for action, last_time in user_cooldowns.items():
                if current_time - last_time > max_age_seconds:
                    actions_to_remove.append(action)
            
            # Remove old actions
            for action in actions_to_remove:
                del user_cooldowns[action]
            
            # Mark user for removal if no actions remain
            if not user_cooldowns:
                users_to_remove.append(user_id)
        
        # Remove users with no remaining cooldowns
        for user_id in users_to_remove:
            del self.user_cooldowns[user_id]
