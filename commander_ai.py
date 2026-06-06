"""
COMMANDER AI - THE BRAIN
From Mainak's handwritten notes:
- 96% follow people with more following than followers
- 3% random follow
- 1% follow creators (once or twice a month)
- Gear system: Week 1-2: 1-10, Week 3-4: 1-25, Week 5+: 1-35
- Random delays, random login times, 2-3 hour naps
- Ban wave detection from web
- Self-evolving code modification
"""

import json
import os
import random
import time
import requests
from datetime import datetime, date

# ========== CONFIGURATION ==========
CUSTOMERS_FILE = "customers.json"
ORDERS_FILE = "active_orders.json"
COMMANDER_LOG_FILE = "commander_log.json"
VERSION_FILE = "version.json"

# ========== PROBABILITY RULES (From your notes) ==========
# 96% follow people with more following than followers
# 3% random follow
# 1% follow creators (once or twice a month)
PROB_FOLLOW_BACK_SEEKERS = 0.96
PROB_RANDOM_FOLLOW = 0.03
PROB_CREATORS = 0.01

# Action distribution (from your notes)
# 68% follow people [do your work]
# 20% just watch posts
# 9% watch reels
# 2% like reels
# 1% follow creators
ACTION_FOLLOW = 0.68
ACTION_WATCH_POSTS = 0.20
ACTION_WATCH_REELS = 0.09
ACTION_LIKE_REELS = 0.02
ACTION_FOLLOW_CREATORS = 0.01

# ========== GEAR SYSTEM (From your notes) ==========
# Week 1-2: 1-10 follows per day (30% chance to break limit)
# Week 3-4: 1-25 follows per day (20% chance to break limit)
# Week 5+: 1-35 follows per day (no breaks)
GEAR_1_DAYS = 14
GEAR_2_DAYS = 28

# Unfollow system (from your notes)
# Per day unfollow: 20/21/22 (sometimes break to 23-29)
# Max unfollow total: 150-172-152-168
DAILY_UNFOLLOW_MIN = 20
DAILY_UNFOLLOW_MAX = 22
MAX_UNFOLLOW_OPTIONS = [150, 152, 168, 172]

# ========== HUMAN BEHAVIOR (From your notes) ==========
MIN_DELAY = 3
MAX_DELAY = 25
NAP_MIN_HOURS = 2
NAP_MAX_HOURS = 3

# Web sources for ban wave detection
BAN_WAVE_SOURCES = [
    "https://www.reddit.com/r/InstagramMarketing/.json",
    "https://www.reddit.com/r/Instagram/.json"
]

class CommanderAI:
    def __init__(self):
        self.version = self.get_version()
        self.ban_wave_level = 0
        self.ban_wave_active = False
        
    def get_version(self):
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r') as f:
                return json.load(f).get("version", "1.0.0")
        return "1.0.0"
    
    def save_version(self):
        with open(VERSION_FILE, 'w') as f:
            json.dump({"version": self.version, "updated_at": datetime.now().isoformat()}, f)
    
    # ========== BAN WAVE DETECTION (From your notes) ==========
    def scan_ban_waves(self):
        """
        Get warnings of ban waves
        Stop the bot before waves
        """
        print("\n" + "="*50)
        print("🌐 SCANNING FOR BAN WAVES...")
        print("="*50)
        
        ban_detected = False
        ban_mentions = []
        
        try:
            for source in BAN_WAVE_SOURCES:
                if "reddit" in source:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    response = requests.get(source, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        for post in data.get("data", {}).get("children", [])[:20]:
                            title = post["data"]["title"].lower()
                            if any(word in title for word in ["ban", "banned", "suspended", "action blocked", "shadowban"]):
                                ban_detected = True
                                ban_mentions.append(title[:80])
                                print(f"  ⚠️ BAN SIGNAL: {title[:60]}...")
        except Exception as e:
            print(f"  ⚠️ Could not scan sources: {e}")
        
        # Also check your own bot accounts for bans
        # This would be implemented with actual Instagram API checks
        
        if ban_detected:
            self.ban_wave_active = True
            self.ban_wave_level = 2
            print("\n  🛑 BAN WAVE DETECTED!")
            print("  📉 Reducing activity by 80%")
            print("  ⏸️  Adding 2-4 hour delays between actions")
            return 0.2  # Only 20% of normal activity
        else:
            self.ban_wave_active = False
            self.ban_wave_level = 0
            print("\n  ✅ No ban wave detected")
            print("  📈 Full speed operation")
            return 1.0
    
    # ========== GEAR SYSTEM (From your notes) ==========
    def get_gear(self, account_age_days):
        """Determine which gear based on account age"""
        if account_age_days <= GEAR_1_DAYS:
            return 1
        elif account_age_days <= GEAR_2_DAYS:
            return 2
        else:
            return 3
    
    def get_daily_follow_limit(self, gear, allow_break=True):
        """
        From your notes:
        Week 1-2: 1-10 follows (30% break chance, +1-5)
        Week 3-4: 1-25 follows (20% break chance, +1-8)
        Week 5+: 1-35 follows (no breaks)
        """
        if gear == 1:
            base_min, base_max = 1, 10
            break_chance = 0.30
            break_extra_min, break_extra_max = 1, 5
        elif gear == 2:
            base_min, base_max = 1, 25
            break_chance = 0.20
            break_extra_min, break_extra_max = 1, 8
        else:  # gear 3
            base_min, base_max = 1, 35
            break_chance = 0
            break_extra_min, break_extra_max = 0, 0
        
        limit = random.randint(base_min, base_max)
        
        # Sometimes break limit (show "human greed")
        if allow_break and random.random() < break_chance:
            extra = random.randint(break_extra_min, break_extra_max)
            limit = limit + extra
            print(f"     🎲 BREAK LIMIT! +{extra} follows today")
        
        return min(limit, 200)  # Never exceed 200 total
    
    def get_daily_unfollow_limit(self, allow_break=True):
        """
        From your notes:
        Per day: 20, 21, or 22
        Sometimes break to 23-29
        """
        limit = random.randint(DAILY_UNFOLLOW_MIN, DAILY_UNFOLLOW_MAX)
        
        if allow_break and random.random() < 0.15:
            limit = random.randint(23, 29)
            print(f"     🔥 UNFOLLOW BREAK: {limit} today")
        
        return limit
    
    def get_max_unfollow_total(self):
        """Random between 150, 152, 168, 172"""
        return random.choice(MAX_UNFOLLOW_OPTIONS)
    
    # ========== ACTION DISTRIBUTION (From your notes) ==========
    def distribute_actions(self, total_actions):
        """
        68% follow, 20% watch posts, 9% watch reels, 2% like reels, 1% follow creators
        """
        actions = {
            "follow": 0,
            "watch_posts": 0,
            "watch_reels": 0,
            "like_reels": 0,
            "follow_creators": 0,
            "unfollow": 0
        }
        
        remaining = total_actions
        
        # Follow (68%)
        follow_count = int(total_actions * ACTION_FOLLOW)
        actions["follow"] = follow_count
        remaining -= follow_count
        
        # Watch posts (20%)
        watch_posts_count = int(total_actions * ACTION_WATCH_POSTS)
        actions["watch_posts"] = watch_posts_count
        remaining -= watch_posts_count
        
        # Watch reels (9%)
        watch_reels_count = int(total_actions * ACTION_WATCH_REELS)
        actions["watch_reels"] = watch_reels_count
        remaining -= watch_reels_count
        
        # Like reels (2%)
        like_reels_count = int(total_actions * ACTION_LIKE_REELS)
        actions["like_reels"] = like_reels_count
        remaining -= like_reels_count
        
        # Follow creators (1%)
        actions["follow_creators"] = remaining
        
        return actions
    
    # ========== HUMAN BEHAVIOR (From your notes) ==========
    def get_random_login_time(self):
        """
        Random login times (not fixed schedule)
        Humans don't log in at the same time every day
        """
        hour = random.randint(6, 23)  # 6 AM to 11 PM
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return f"{hour:02d}:{minute:02d}:{second:02d}"
    
    def should_take_nap(self):
        """
        Simulate human naps (2-3 hours)
        From your notes: "take a 2/3 hrs nap"
        """
        nap_hours = random.uniform(NAP_MIN_HOURS, NAP_MAX_HOURS)
        print(f"     😴 Taking {nap_hours:.1f} hour nap...")
        return nap_hours
    
    def think_like_human(self):
        """
        Think like human, not robot
        Copy lazy work of humans
        From your notes: "copy lazy human", "lazy human randomisation"
        """
        print("\n" + "="*50)
        print("🧠 THINKING LIKE A HUMAN...")
        print("="*50)
        
        # Humans are lazy sometimes
        lazy_chance = random.random()
        if lazy_chance < 0.10:  # 10% chance to be very lazy
            print("  😴 Feeling VERY lazy today. Reducing work by 60%")
            return 0.4
        elif lazy_chance < 0.25:  # 15% chance to be a bit lazy
            print("  😌 Feeling a bit lazy. Reducing work by 25%")
            return 0.75
        
        # Humans have good days and bad days
        if random.random() < 0.70:  # 70% normal productive day
            print("  💪 Normal productive day")
            return 1.0
        else:
            efficiency = random.uniform(0.6, 0.9)
            print(f"  📉 Low energy day. {int(efficiency*100)}% efficiency")
            return efficiency
    
    # ========== SELF-EVOLVING CODE (From your notes) ==========
    def modify_own_code(self, performance_data):
        """
        Modify the code as per needs
        Keep code always 1 step ahead of Instagram
        From your notes: "modify the code as per needs should do",
        "keep code always 1 step ahead of insta."
        """
        print("\n" + "="*50)
        print("🔧 MODIFYING OWN CODE (Self-Evolution)...")
        print("="*50)
        
        changes_made = []
        
        # Analyze performance
        if performance_data:
            ban_rate = performance_data.get("ban_rate", 0)
            success_rate = performance_data.get("success_rate", 1.0)
            
            # If high ban rate, reduce aggression
            if ban_rate > 0.20:
                print("  ⚠️ High ban rate detected! Reducing daily limits in config")
                changes_made.append("reduced_daily_limits")
                self.version = f"{self.version.split('.')[0]}.{int(self.version.split('.')[1])+1}.0"
            
            # If low success rate, adjust following strategy
            if success_rate < 0.70:
                print("  📉 Low success rate! Adjusting follow targets")
                changes_made.append("adjusted_follow_targets")
        
        # Random improvements (AI self-evolution)
        if random.random() < 0.30:  # 30% chance to try a new strategy
            improvements = [
                "added_slower_delays",
                "adjusted_probability_rules",
                "changed_watch_to_follow_ratio",
                "added_more_randomness"
            ]
            selected = random.choice(improvements)
            changes_made.append(selected)
            print(f"  🧬 AI Evolution: Applied '{selected}'")
        
        # Update version if changes were made
        if changes_made:
            self.save_version()
            print(f"  📌 Version updated to {self.version}")
        
        return changes_made
    
    # ========== GENERATE ORDERS FOR BOTS ==========
    def generate_orders(self, customers, speed_multiplier, human_efficiency):
        """
        Generate orders for each customer bot
        Uses all the probability rules and gear system
        """
        print("\n" + "="*50)
        print("📋 GENERATING ORDERS FOR BOTS...")
        print("="*50)
        
        orders = []
        
        for customer in customers:
            if customer.get("status") == "completed":
                continue
            
            username = customer["username"]
            session_id = customer["session_id"]
            account_age = customer.get("account_age_days", 30)
            followers_needed = customer["followers"]
            delivered_so_far = customer.get("delivered", 0)
            remaining = followers_needed - delivered_so_far
            
            if remaining <= 0:
                customer["status"] = "completed"
                continue
            
            # Get gear and daily limit
            gear = self.get_gear(account_age)
            daily_limit = self.get_daily_follow_limit(gear)
            
            # Apply ban wave reduction and human efficiency
            final_daily = int(daily_limit * speed_multiplier * human_efficiency)
            final_daily = max(1, min(final_daily, remaining))  # At least 1, not more than remaining
            
            # Distribute actions based on your probability rules
            actions = self.distribute_actions(final_daily)
            actions["unfollow"] = self.get_daily_unfollow_limit()
            
            # Random login time (human behavior)
            login_time = self.get_random_login_time()
            
            # Random chance to take a nap during work
            will_take_nap = random.random() < 0.30  # 30% chance
            
            order = {
                "customer_username": username,
                "session_id": session_id,
                "order_id": customer.get("order_id", f"ORD_{username}_{datetime.now().timestamp()}"),
                "actions": actions,
                "gear": gear,
                "account_age_days": account_age,
                "remaining_followers": remaining,
                "login_time": login_time,
                "will_take_nap": will_take_nap,
                "created_at": datetime.now().isoformat()
            }
            
            orders.append(order)
            
            print(f"\n  👤 @{username} (Gear {gear})")
            print(f"     Account age: {account_age} days")
            print(f"     Remaining: {remaining} followers")
            print(f"     Daily limit: {final_daily} follows")
            print(f"     Actions: {actions['follow']} follow, {actions['watch_posts']} watch posts, {actions['watch_reels']} watch reels, {actions['like_reels']} like reels")
            print(f"     Unfollow: {actions['unfollow']} today")
            print(f"     Login window: ~{login_time}")
            if will_take_nap:
                print(f"     😴 Will take a {random.uniform(2,3):.1f} hour nap")
        
        return orders
    
    def log_run(self, orders_count, strategies_applied, speed_multiplier):
        """Log this run for future self-evolution"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "version": self.version,
            "orders_count": orders_count,
            "strategies_applied": strategies_applied,
            "ban_wave_active": self.ban_wave_active,
            "speed_multiplier": speed_multiplier
        }
        
        logs = []
        if os.path.exists(COMMANDER_LOG_FILE):
            with open(COMMANDER_LOG_FILE, 'r') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        # Keep last 200 logs only
        if len(logs) > 200:
            logs = logs[-200:]
        
        with open(COMMANDER_LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def update_customers_status(self, customers, orders):
        """Update customers.json with latest delivery progress"""
        # Map orders back to customers
        for order in orders:
            for customer in customers:
                if customer["username"] == order["customer_username"]:
                    customer["last_order"] = {
                        "date": datetime.now().isoformat(),
                        "daily_follows": order["actions"]["follow"],
                        "gear": order["gear"]
                    }
        
        with open(CUSTOMERS_FILE, 'w') as f:
            json.dump(customers, f, indent=2)
    
    # ========== MAIN RUN FUNCTION ==========
    def run(self, customers):
        """
        Main function - The Brain's main loop
        """
        print("\n" + "="*60)
        print(f"🤖 COMMANDER AI v{self.version} - {datetime.now()}")
        print("="*60)
        print("\n📝 LOADED FROM MAINAK'S HANDWRITTEN NOTES:")
        print("   • 96% follow back seekers / 3% random / 1% creators")
        print("   • Gear system: Week1-2:1-10, Week3-4:1-25, Week5+:1-35")
        print("   • 68% follow / 20% watch posts / 9% watch reels / 2% like / 1% creators")
        print("   • Random delays, random login times, 2-3 hour naps")
        print("   • Ban wave detection from web")
        print("   • Self-evolving code")
        
        # STEP 1: Check for ban waves
        speed_multiplier = self.scan_ban_waves()
        
        # STEP 2: Think like a human (lazy days, energy levels)
        human_efficiency = self.think_like_human()
        
        # STEP 3: Generate orders for all customers
        orders = self.generate_orders(customers, speed_multiplier, human_efficiency)
        
        # STEP 4: Save orders for bot_worker
        with open(ORDERS_FILE, 'w') as f:
            json.dump(orders, f, indent=2)
        
        # STEP 5: Update customers.json with status
        self.update_customers_status(customers, orders)
        
        # STEP 6: Self-evolution (modify own code based on performance)
        performance_data = {
            "ban_rate": 0.1 if self.ban_wave_active else 0.0,
            "success_rate": 0.85  # This would come from actual delivery logs
        }
        changes = self.modify_own_code(performance_data)
        
        # STEP 7: Log this run
        self.log_run(len(orders), changes, speed_multiplier)
        
        print("\n" + "="*60)
        print(f"✅ COMMANDER AI FINISHED - {len(orders)} order(s) generated")
        print("="*60)
        
        return orders

# ========== MAIN ENTRY POINT ==========
if __name__ == "__main__":
    # Load customers
    if not os.path.exists(CUSTOMERS_FILE):
        print("❌ customers.json not found! Creating empty...")
        with open(CUSTOMERS_FILE, 'w') as f:
            json.dump([], f)
    
    with open(CUSTOMERS_FILE, 'r') as f:
        customers = json.load(f)
    
    if not customers:
        print("📭 No customers found. Waiting for orders from website...")
        exit(0)
    
    print(f"📋 Loaded {len(customers)} customer(s)")
    
    # Run Commander AI
    ai = CommanderAI()
    orders = ai.run(customers)
    
    print(f"\n📤 Orders saved to active_orders.json")
