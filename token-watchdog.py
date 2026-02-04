#!/usr/bin/env python3
"""
Token Watchdog - Monitor and alert on inefficient processing
"""

import time
import json
import threading
from datetime import datetime, timedelta
import os
from pathlib import Path

class TokenWatchdog:
    def __init__(self, workspace_path="/Users/clawdbot/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.monitoring = False
        self.start_time = None
        self.task_name = None
        self.alerts_sent = []
        
        # Thresholds
        self.WARNING_TIME = 30  # seconds
        self.CRITICAL_TIME = 60  # seconds
        self.MAX_TIME = 120     # seconds - auto-abort
        
    def start_task(self, task_name, expected_duration=30):
        """Start monitoring a task"""
        self.task_name = task_name
        self.start_time = time.time()
        self.monitoring = True
        self.expected_duration = expected_duration
        
        # Start background monitor
        threading.Thread(target=self._monitor_task, daemon=True).start()
        
        # Log task start
        self._log_event("TASK_START", {
            "task": task_name,
            "expected_duration": expected_duration,
            "timestamp": datetime.now().isoformat()
        })
        
    def end_task(self, success=True, notes=None):
        """End task monitoring"""
        if not self.monitoring:
            return
            
        self.monitoring = False
        duration = time.time() - self.start_time if self.start_time else 0
        
        self._log_event("TASK_END", {
            "task": self.task_name,
            "duration": duration,
            "success": success,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        })
        
        # Send completion alert if task took too long
        if duration > self.expected_duration * 2:
            self._send_alert(
                "INEFFICIENT_TASK",
                f"Task '{self.task_name}' took {duration:.1f}s (expected {self.expected_duration}s)",
                "medium"
            )
    
    def _monitor_task(self):
        """Background monitoring thread"""
        while self.monitoring and self.start_time:
            elapsed = time.time() - self.start_time
            
            # Warning threshold
            if elapsed > self.WARNING_TIME and "warning" not in self.alerts_sent:
                self._send_alert(
                    "PROCESSING_SLOW", 
                    f"Task '{self.task_name}' running {elapsed:.1f}s - may be inefficient",
                    "low"
                )
                self.alerts_sent.append("warning")
            
            # Critical threshold  
            elif elapsed > self.CRITICAL_TIME and "critical" not in self.alerts_sent:
                self._send_alert(
                    "PROCESSING_STUCK",
                    f"Task '{self.task_name}' stuck at {elapsed:.1f}s - consider manual intervention",
                    "high"
                )
                self.alerts_sent.append("critical")
            
            # Auto-abort threshold
            elif elapsed > self.MAX_TIME:
                self._send_alert(
                    "TASK_ABORTED",
                    f"Auto-aborting '{self.task_name}' after {elapsed:.1f}s to prevent token waste",
                    "critical"
                )
                self.monitoring = False
                break
                
            time.sleep(5)  # Check every 5 seconds
    
    def _send_alert(self, alert_type, message, priority):
        """Send alert to user"""
        alert = {
            "type": alert_type,
            "message": message,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "task": self.task_name,
            "elapsed": time.time() - self.start_time if self.start_time else 0
        }
        
        # Write alert file for immediate pickup
        alert_file = self.workspace / f"alert_{int(time.time())}.json"
        with open(alert_file, 'w') as f:
            json.dump(alert, f, indent=2)
        
        # Also append to alerts log
        self._log_event("ALERT", alert)
        
        print(f"🚨 ALERT: {message}")
    
    def _log_event(self, event_type, data):
        """Log events to monitoring file"""
        log_file = self.workspace / "token-monitoring.jsonl"
        
        entry = {
            "event": event_type,
            "timestamp": datetime.now().isoformat(),
            **data
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

# Global watchdog instance
watchdog = TokenWatchdog()

def monitor_task(task_name, expected_duration=30):
    """Decorator to monitor task execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            watchdog.start_task(task_name, expected_duration)
            try:
                result = func(*args, **kwargs)
                watchdog.end_task(success=True)
                return result
            except Exception as e:
                watchdog.end_task(success=False, notes=str(e))
                raise
        return wrapper
    return decorator

# Usage examples:
# watchdog.start_task("web_search", 15)
# ... do work ...
# watchdog.end_task()

if __name__ == "__main__":
    # Demo the system
    print("🔍 Testing Token Watchdog...")
    
    watchdog.start_task("demo_task", 10)
    time.sleep(35)  # Simulate long task
    watchdog.end_task()
    
    print("✅ Demo complete - check token-monitoring.jsonl for logs")