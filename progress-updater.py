#!/usr/bin/env python3
"""
Progress Updater - Send progress updates during long tasks
"""

import json
import time
from pathlib import Path

class ProgressUpdater:
    def __init__(self):
        self.workspace = Path("/Users/clawdbot/.openclaw/workspace")
        
    def update(self, task_name, progress_pct, status_msg, estimated_remaining=None):
        """Send progress update"""
        update = {
            "task": task_name,
            "progress": progress_pct,
            "status": status_msg,
            "timestamp": time.time(),
            "estimated_remaining": estimated_remaining
        }
        
        # Write progress file
        progress_file = self.workspace / "current_progress.json"
        with open(progress_file, 'w') as f:
            json.dump(update, f, indent=2)
            
        # Send to user
        print(f"📊 {task_name}: {progress_pct}% - {status_msg}")
        if estimated_remaining:
            print(f"   ⏱️ Est. {estimated_remaining}s remaining")
    
    def complete(self, task_name, success=True, final_message=None):
        """Mark task complete"""
        # Clean up progress file
        progress_file = self.workspace / "current_progress.json"
        if progress_file.exists():
            progress_file.unlink()
            
        status = "✅ Complete" if success else "❌ Failed"
        print(f"{status}: {task_name}")
        if final_message:
            print(f"   {final_message}")

# Global updater
progress = ProgressUpdater()

# Quick usage functions
def progress_update(task, pct, msg, remaining=None):
    progress.update(task, pct, msg, remaining)

def progress_complete(task, success=True, msg=None):
    progress.complete(task, success, msg)

if __name__ == "__main__":
    # Demo
    import time
    
    for i in range(0, 101, 20):
        progress_update("Demo Task", i, f"Processing step {i//20 + 1}/5", (100-i)*0.5)
        time.sleep(1)
    
    progress_complete("Demo Task", True, "All steps completed successfully")