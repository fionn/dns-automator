#!/usr/bin/env python3
"""dns_automator runner"""

from app import create_app

def main() -> None:
    """Entry point"""
    app = create_app()
    app.run(debug=True)

if __name__ == "__main__":
    main()
