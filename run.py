"""
Local development entry point — loads .env then starts the bot in polling mode.
On Railway, the Procfile runs bot.py directly (no .env needed there).

Run locally:  python run.py
"""
from dotenv import load_dotenv
load_dotenv()

from bot import main

if __name__ == "__main__":
    main()
