# main.py

from game.engine import run_game   # ← без скобок!

if __name__ == "__main__":
    try:
        run_game()
    except KeyboardInterrupt:
        print("Выход по Ctrl+C")

