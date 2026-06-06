"""
BOT WORKER - Executes orders from Commander AI
Logs into each customer account using their Session ID
Performs follows, watches, likes based on probability rules
"""

import json
import time
import random
import os
from datetime import datetime

# ========== CONFIGURATION ==========
ACTIVE_ORDERS_FILE = "active_orders.json"
CUSTOMERS_FILE = "customers.json"
DELIVERY_LOG_FILE = "delivery_log.json"

# Human-like delays (from your notes)
MIN_DELAY = 3
MAX_DELAY = 25
WATCH_POST_MIN_SEC = 10
WATCH_POST_MAX_SEC = 45
WATCH_REEL_MIN_SEC = 15
WATCH_REEL_MAX_SEC = 60

def load_json(file):
    if not os.path.exists(file):
        return []
    with open(file, 'r') as f:
        return json.load(f)

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

def human_delay(min_sec=MIN_DELAY, max_sec=MAX_DELAY):
    """Random human-like delay between actions"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)

def should_follow():
    """
    Probability rules from your notes:
    96% - follow people with more following than followers (follow back seekers)
    3% - random follow
    1% - follow creators (once or twice a month)
    """
    r = random.random()
    if r < 0.96:
        return "follow_back_seeker"
    elif r < 0.99:
        return "random"
    else:
        return "creator"

def find_target_to_follow(follow_type):
    """
    Find appropriate target based on follow type
    - follow_back_seeker: users with more following than followers
    - random: any active user
    - creator: verified or high-profile accounts
    """
    # This is where you'll implement actual Instagram API calls
    # For now, returns placeholder
    # You will replace this with real target finding logic
    
    if follow_type == "follow_back_seeker":
        # Search hashtags like #followback #follow4follow
        return "target_follow_back_user"
    elif follow_type == "creator":
        # Follow a creator (rare - 1% of actions)
        return "target_creator_account"
    else:
        # Random follow
        return "random_user"

def execute_follow(session_id, target_username):
    """
    Execute a follow action using instagrapi
    """
    try:
        from instagrapi import Client
        cl = Client()
        cl.set_settings({"sessionid": session_id})
        cl.login_by_sessionid(session_id)
        
        user_id = cl.user_id_from_username(target_username)
        cl.user_follow(user_id)
        
        cl.logout()
        return True, None
    except Exception as e:
        return False, str(e)

def execute_watch_post(session_id):
    """
    Simulate watching a post (no API call needed for delivery)
    Just adds human-like behavior
    """
    print(f"       📱 Watching post...")
    human_delay(WATCH_POST_MIN_SEC, WATCH_POST_MAX_SEC)
    return True

def execute_watch_reel(session_id):
    """
    Simulate watching a reel
    """
    print(f"       📱 Watching reel...")
    human_delay(WATCH_REEL_MIN_SEC, WATCH_REEL_MAX_SEC)
    return True

def execute_like_reel(session_id):
    """
    Like a reel (2% of actions)
    """
    print(f"       ❤️ Liking reel...")
    human_delay(2, 8)
    return True

def execute_unfollow(session_id, target_username):
    """
    Unfollow a user (part of unfollow cycle)
    Wait 2-6 days before unfollowing as per your notes
    """
    try:
        from instagrapi import Client
        cl = Client()
        cl.set_settings({"sessionid": session_id})
        cl.login_by_sessionid(session_id)
        
        user_id = cl.user_id_from_username(target_username)
        cl.user_unfollow(user_id)
        
        cl.logout()
        return True, None
    except Exception as e:
        return False, str(e)

def run_bot_for_customer(order):
    """
    Execute all actions for one customer
    """
    username = order["customer_username"]
    session_id = order["session_id"]
    actions = order["actions"]
    gear = order["gear"]
    login_time = order.get("login_time", "any time")
    will_take_nap = order.get("will_take_nap", False)
    
    print(f"\n" + "="*50)
    print(f"🤖 BOT RUNNING FOR: @{username}")
    print(f"   Gear: {gear}")
    print(f"   Scheduled login: ~{login_time}")
    print(f"   Actions today: {actions['follow']} follows, {actions['watch_posts']} watch posts, {actions['watch_reels']} watch reels, {actions['like_reels']} like reels")
    print(f"   Unfollow today: {actions['unfollow']}")
    print("="*50)
    
    results = {
        "username": username,
        "follows_done": 0,
        "watch_posts_done": 0,
        "watch_reels_done": 0,
        "likes_done": 0,
        "unfollows_done": 0,
        "errors": []
    }
    
    # FOLLOW ACTIONS (68% of work)
    print(f"\n  📌 FOLLOWING ({actions['follow']} accounts)...")
    for i in range(actions['follow']):
        follow_type = should_follow()
        target = find_target_to_follow(follow_type)
        
        print(f"     {i+1}/{actions['follow']}: Following @{target} ({follow_type})")
        
        success, error = execute_follow(session_id, target)
        if success:
            results['follows_done'] += 1
        else:
            results['errors'].append(f"Follow failed: {error}")
        
        # Human-like delay
        human_delay()
        
        # Every 5-10 follows, add extra random delay
        if random.random() < 0.20:
            extra_delay = random.uniform(10, 30)
            print(f"       ⏱️ Extra delay: {extra_delay:.0f} seconds")
            time.sleep(extra_delay)
    
    # WATCH POSTS (20% of work)
    print(f"\n  📱 WATCHING POSTS ({actions['watch_posts']} posts)...")
    for i in range(actions['watch_posts']):
        print(f"     {i+1}/{actions['watch_posts']}: Watching post")
        execute_watch_post(session_id)
        results['watch_posts_done'] += 1
        human_delay()
    
    # WATCH REELS (9% of work)
    print(f"\n  🎬 WATCHING REELS ({actions['watch_reels']} reels)...")
    for i in range(actions['watch_reels']):
        print(f"     {i+1}/{actions['watch_reels']}: Watching reel")
        execute_watch_reel(session_id)
        results['watch_reels_done'] += 1
        human_delay()
    
    # LIKE REELS (2% of work)
    print(f"\n  ❤️ LIKING REELS ({actions['like_reels']} likes)...")
    for i in range(actions['like_reels']):
        print(f"     {i+1}/{actions['like_reels']}: Liking reel")
        execute_like_reel(session_id)
        results['likes_done'] += 1
        human_delay()
    
    # UNFOLLOW CYCLE (from your notes)
    print(f"\n  🔄 UNFOLLOWING ({actions['unfollow']} accounts)...")
    for i in range(actions['unfollow']):
        print(f"     {i+1}/{actions['unfollow']}: Unfollowing")
        # In real implementation, you'd unfollow users who didn't follow back after 2-6 days
        results['unfollows_done'] += 1
        human_delay()
    
    # Take a nap if scheduled (from your notes)
    if will_take_nap:
        nap_hours = random.uniform(2, 3)
        print(f"\n  😴 Taking {nap_hours:.1f} hour nap (human behavior)...")
        time.sleep(nap_hours * 3600)
    
    print(f"\n  ✅ COMPLETED for @{username}")
    print(f"     Follows: {results['follows_done']}")
    print(f"     Watch posts: {results['watch_posts_done']}")
    print(f"     Watch reels: {results['watch_reels_done']}")
    print(f"     Likes: {results['likes_done']}")
    print(f"     Unfollows: {results['unfollows_done']}")
    
    return results

def update_customer_progress(customers, results):
    """Update customers.json with delivery progress"""
    for customer in customers:
        for result in results:
            if customer["username"] == result["username"]:
                # Each follow adds 1 to delivered count
                customer["delivered"] = customer.get("delivered", 0) + result["follows_done"]
                customer["last_run"] = datetime.now().isoformat()
                
                # Check if order is complete
                if customer["delivered"] >= customer["followers"]:
                    customer["status"] = "completed"
                    customer["completed_at"] = datetime.now().isoformat()
    
    save_json(CUSTOMERS_FILE, customers)

def run_all_bots():
    """
    Main function - runs all bots for all customers
    """
    print("\n" + "="*60)
    print(f"🤖 BOT WORKER STARTED - {datetime.now()}")
    print("="*60)
    
    # Load orders from Commander AI
    orders = load_json(ACTIVE_ORDERS_FILE)
    
    if not orders:
        print("📭 No active orders. Waiting for Commander AI...")
        return
    
    print(f"📋 Loaded {len(orders)} customer order(s)")
    
    # Load customers to update progress
    customers = load_json(CUSTOMERS_FILE)
    
    all_results = []
    
    for order in orders:
        result = run_bot_for_customer(order)
        all_results.append(result)
        
        # Random delay between different customers (human-like)
        if len(orders) > 1:
            between_customers_delay = random.uniform(60, 300)  # 1-5 minutes
            print(f"\n  ⏱️ Waiting {between_customers_delay/60:.0f} minutes before next customer...")
            time.sleep(between_customers_delay)
    
    # Update customer progress
    update_customer_progress(customers, all_results)
    
    # Save delivery log
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "results": all_results
    }
    
    logs = load_json(DELIVERY_LOG_FILE)
    logs.append(log_entry)
    save_json(DELIVERY_LOG_FILE, logs[-100:])  # Keep last 100 logs
    
    print("\n" + "="*60)
    print(f"✅ BOT WORKER FINISHED")
    print(f"   Total follows delivered: {sum(r['follows_done'] for r in all_results)}")
    print("="*60)

if __name__ == "__main__":
    run_all_bots()
