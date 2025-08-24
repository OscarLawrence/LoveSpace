#!/usr/bin/env python3
"""
Trading System Runner Script
Orchestrates the micro-trading bot with background process support.
"""

import os
import sys
import time
import signal
import argparse
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, assume env vars already set

# Add trading_system to path
sys.path.insert(0, str(Path(__file__).parent / "trading_system"))

from trading_system import MicroTradingBot


class TradingSystemRunner:
    """Main runner for the trading system with process management."""
    
    def __init__(self):
        self.bot: Optional[MicroTradingBot] = None
        self.background_process: Optional[subprocess.Popen] = None
        self.pid_file = Path.home() / ".trading_bot.pid"
        
    def setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers."""
        def signal_handler(signum, frame):
            print(f"\nReceived signal {signum}, shutting down gracefully...")
            self.stop_trading()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def check_credentials(self) -> bool:
        """Verify Binance API credentials are configured."""
        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_API_SECRET")
        
        if not api_key or not api_secret:
            print("❌ Binance API credentials not found!")
            print("Please set environment variables:")
            print("  export BINANCE_API_KEY='your_api_key'")
            print("  export BINANCE_API_SECRET='your_api_secret'")
            print("  export BINANCE_TESTNET='true'  # Optional, defaults to true")
            return False
        
        testnet = os.getenv("BINANCE_TESTNET", "true").lower() == "true"
        env_type = "testnet" if testnet else "live"
        print(f"✅ Binance API credentials found ({env_type} mode)")
        return True
    
    def run_trading_bot(self, duration_hours: int = 24):
        """Run the trading bot directly."""
        print(f"🚀 Starting MicroTradingBot for {duration_hours} hours...")
        print(f"📊 Timestamp: {datetime.now()}")
        
        try:
            self.bot = MicroTradingBot()
            self.bot.run(duration_hours=duration_hours)
            
        except KeyboardInterrupt:
            print("\n⏹️  Trading stopped by user")
        except Exception as e:
            print(f"❌ Trading error: {e}")
        finally:
            print("🏁 Trading session completed")
    
    def start_background(self, duration_hours: int = 24):
        """Start trading bot as background process."""
        if self.is_running():
            print("❌ Trading bot is already running in background")
            return False
        
        print(f"🌙 Starting trading bot in background for {duration_hours} hours...")
        
        # Create background process
        script_path = Path(__file__).absolute()
        cmd = [
            sys.executable, 
            str(script_path), 
            "run", 
            "--duration", str(duration_hours)
        ]
        
        try:
            self.background_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(self.background_process.pid))
            
            print(f"✅ Trading bot started in background (PID: {self.background_process.pid})")
            print(f"📁 Logs will be written to: trading_bot.log")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start background process: {e}")
            return False
    
    def stop_background(self):
        """Stop background trading process."""
        if not self.is_running():
            print("❌ No trading bot running in background")
            return False
        
        try:
            # Read PID from file
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Send termination signal
            os.kill(pid, signal.SIGTERM)
            
            # Wait a moment for graceful shutdown
            time.sleep(2)
            
            # Force kill if still running
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # Process already terminated
            
            # Clean up PID file
            self.pid_file.unlink(missing_ok=True)
            
            print("⏹️  Background trading bot stopped")
            return True
            
        except Exception as e:
            print(f"❌ Failed to stop background process: {e}")
            return False
    
    def is_running(self) -> bool:
        """Check if trading bot is running in background."""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            os.kill(pid, 0)
            return True
            
        except (ProcessLookupError, ValueError, FileNotFoundError):
            # Clean up stale PID file
            self.pid_file.unlink(missing_ok=True)
            return False
    
    def status(self):
        """Show trading bot status."""
        if self.is_running():
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            print(f"✅ Trading bot is running (PID: {pid})")
            
            # Show recent log entries if available
            log_file = Path("trading_bot.log")
            if log_file.exists():
                print("\n📊 Recent log entries:")
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        for line in lines[-5:]:  # Last 5 lines
                            print(f"  {line.strip()}")
                except Exception:
                    pass
        else:
            print("❌ Trading bot is not running")
    
    def stop_trading(self):
        """Stop any running trading process."""
        if self.bot:
            print("⏹️  Stopping direct trading...")
        
        if self.is_running():
            self.stop_background()


def main():
    """Main entry point with CLI interface."""
    parser = argparse.ArgumentParser(description="MomoAI Trading System Runner")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run trading bot directly")
    run_parser.add_argument("--duration", type=int, default=24, 
                           help="Trading duration in hours (default: 24)")
    
    # Background commands
    start_parser = subparsers.add_parser("start", help="Start trading bot in background")
    start_parser.add_argument("--duration", type=int, default=24,
                             help="Trading duration in hours (default: 24)")
    
    subparsers.add_parser("stop", help="Stop background trading bot")
    subparsers.add_parser("status", help="Show trading bot status")
    subparsers.add_parser("restart", help="Restart background trading bot")
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = TradingSystemRunner()
    runner.setup_signal_handlers()
    
    # Verify credentials for all commands except status
    if args.command != "status" and not runner.check_credentials():
        sys.exit(1)
    
    # Execute command
    if args.command == "run":
        runner.run_trading_bot(args.duration)
    
    elif args.command == "start":
        runner.start_background(args.duration)
    
    elif args.command == "stop":
        runner.stop_background()
    
    elif args.command == "status":
        runner.status()
    
    elif args.command == "restart":
        runner.stop_background()
        time.sleep(1)
        runner.start_background(24)
    
    else:
        print("🤖 MomoAI Trading System")
        print("=" * 40)
        print("Available commands:")
        print("  run [--duration HOURS]    Run trading bot directly")
        print("  start [--duration HOURS]  Start in background")
        print("  stop                      Stop background bot")
        print("  status                    Show bot status")
        print("  restart                   Restart background bot")
        print()
        print("Examples:")
        print("  python run_trading_system.py run --duration 8")
        print("  python run_trading_system.py start")
        print("  python run_trading_system.py status")


if __name__ == "__main__":
    main()