"""Backward-compatible entrypoint — delegates to production generator."""
from producer.payment_generator import run

if __name__ == "__main__":
    run()
