#!/usr/bin/env python3
"""
MomoAI Background Trading Daemon
Runs the coherent trading system continuously in the background.
"""

import os
import sys
import time
import json
import signal
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path


class TradingDaemon:
    """Background trading daemon with process management."""
    
    def __init__(self):
        self.pid_file = Path.home() / ".momoai_trader.pid"
        self.log_file = Path.cwd() / "momoai_trader.log"
        self.status_file = Path.cwd() / "trader_status.json"
        self.process = None
        
        # Setup daemon logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def is_running(self) -> bool:
        """Check if trading daemon is running."""
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
    
    def start_daemon(self):
        """Start the trading daemon."""
        if self.is_running():
            self.logger.error("❌ Trading daemon is already running")
            return False
        
        self.logger.info("🚀 Starting MomoAI Trading Daemon...")
        
        try:
            # Start background process
            script_path = Path(__file__).parent / "daemon_trader.py"
            
            self.process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
                cwd=Path(__file__).parent
            )
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(self.process.pid))
            
            # Initial status
            self.update_status("starting")
            
            self.logger.info(f"✅ Trading daemon started (PID: {self.process.pid})")
            self.logger.info(f"📁 Logs: {self.log_file}")
            self.logger.info(f"📊 Status: {self.status_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start daemon: {e}")
            return False
    
    def stop_daemon(self):
        """Stop the trading daemon."""
        if not self.is_running():
            self.logger.error("❌ No trading daemon running")
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            self.logger.info(f"⏹️ Stopping trading daemon (PID: {pid})")
            
            # Send termination signal
            os.kill(pid, signal.SIGTERM)
            
            # Wait for graceful shutdown
            for i in range(10):
                try:
                    os.kill(pid, 0)
                    time.sleep(1)
                except ProcessLookupError:
                    break
            else:
                # Force kill if still running
                self.logger.warning("🔪 Force killing daemon")
                os.kill(pid, signal.SIGKILL)
            
            # Clean up
            self.pid_file.unlink(missing_ok=True)
            self.update_status("stopped")
            
            self.logger.info("✅ Trading daemon stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop daemon: {e}")
            return False
    
    def restart_daemon(self):
        """Restart the trading daemon."""
        self.logger.info("🔄 Restarting trading daemon...")
        self.stop_daemon()
        time.sleep(2)
        return self.start_daemon()
    
    def show_status(self):
        """Show daemon status and recent performance."""
        print("📊 MOMOAI TRADING DAEMON STATUS")
        print("=" * 50)
        
        # Process status
        if self.is_running():
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            print(f"🟢 Status: RUNNING (PID: {pid})")
        else:
            print(f"🔴 Status: STOPPED")
        
        # Load status file
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    status = json.load(f)
                
                print(f"\n💰 Trading Performance:")
                print(f"   Start Balance: ${status.get('start_balance', 0):.2f}")
                print(f"   Current Balance: ${status.get('current_balance', 0):.2f}")
                print(f"   Total P&L: ${status.get('total_pnl', 0):.2f}")
                print(f"   Total Trades: {status.get('total_trades', 0)}")
                print(f"   Last Update: {status.get('last_update', 'Never')}")
                
                if status.get('recent_trades'):
                    print(f"\n📈 Recent Trades:")
                    for trade in status['recent_trades'][-5:]:
                        print(f"   {trade['timestamp']}: {trade['strategy']} - ${trade.get('pnl', 0):+.2f}")
                
            except Exception as e:
                print(f"⚠️ Could not read status: {e}")
        
        # Recent logs
        if self.log_file.exists():
            print(f"\n📋 Recent Log Entries:")
            try:
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-10:]:  # Last 10 lines
                        print(f"   {line.strip()}")
            except Exception:
                print("   Could not read log file")
        
        print("=" * 50)
    
    def update_status(self, status: str, data: dict = None):
        """Update status file."""
        try:
            status_data = {
                'status': status,
                'last_update': datetime.now().isoformat(),
                'pid': self.process.pid if self.process else None
            }
            
            if data:
                status_data.update(data)
            
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to update status: {e}")


def main():
    """Main daemon controller."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MomoAI Trading Daemon Controller")
    parser.add_argument("command", choices=["start", "stop", "restart", "status"], 
                       help="Daemon command")
    
    args = parser.parse_args()
    
    daemon = TradingDaemon()
    
    if args.command == "start":
        success = daemon.start_daemon()
        if success:
            print("🚀 MomoAI Trading Daemon started successfully!")
            print("💡 Use 'python background_trader.py status' to monitor")
        sys.exit(0 if success else 1)
        
    elif args.command == "stop":
        success = daemon.stop_daemon()
        sys.exit(0 if success else 1)
        
    elif args.command == "restart":
        success = daemon.restart_daemon()
        sys.exit(0 if success else 1)
        
    elif args.command == "status":
        daemon.show_status()


if __name__ == "__main__":
    main()