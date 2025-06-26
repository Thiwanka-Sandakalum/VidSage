#!/usr/bin/env python3
"""
VidSage - Main Entry Point

This script serves as the entry point for the VidSage application.
It imports and runs the enhanced CLI interface.
"""

import sys

def main():
    """Main entry point with enhanced CLI option"""
    try:
        # Try to use the enhanced CLI first
        from cli.enhanced_main_complete import main as enhanced_main
        enhanced_main()
    except ImportError as e:
        print(f"Enhanced CLI not available ({e}), falling back to standard CLI...")
        try:
            # Fallback to standard CLI
            from cli.main import main as standard_main
            standard_main()
        except ImportError as e2:
            print(f"Standard CLI also not available ({e2})")
            sys.exit(1)
    except Exception as e:
        print(f"Error starting VidSage: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
