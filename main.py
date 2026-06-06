"""
GODBOT MAIN ORCHESTRATOR
Runs Commander AI (The Brain), then Bot Workers (The Muscles)
"""

import os
import json
import subprocess
from datetime import datetime

print("\n" + "="*60)
print(f"🦾 GODBOT SYSTEM STARTED - {datetime.now()}")
print("="*60)
print("\n📝 SYSTEM FEATURES:")
print("   • Commander AI (The Brain) with all probability rules")
print("   • 96% follow back seekers / 3% random / 1% creators")
print("   • Gear system (Week1-2:1-10, Week3-4:1-25, Week5+:1-35)")
print("   • 68% follow / 20% watch posts / 9% watch reels / 2% like / 1% creators")
print("   • Human-like delays, random login times, 2-3 hour naps")
print("   • Ban wave detection from web")
print("   • Self-evolving code modification")

# STEP 1: Run Commander AI (The Brain)
print("\n" + "-"*50)
print("[1/2] STARTING COMMANDER AI (THE BRAIN)...")
print("-"*50)

os.system("python commander_ai.py")

# STEP 2: Run Bot Workers (Execute deliveries)
print("\n" + "-"*50)
print("[2/2] STARTING BOT WORKERS (EXECUTION)...")
print("-"*50)

os.system("python bot_worker.py")

print("\n" + "="*60)
print(f"✅ GODBOT SYSTEM FINISHED - {datetime.now()}")
print("="*60)
