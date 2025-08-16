#!/usr/bin/env python3
"""
Flow-Respecting Notification Queue for Luminous Nix.

Implements the 2-minute rule: batch non-critical notifications to prevent
interrupting user flow state. Based on research showing context switching
reduces productivity by 47%.

Simple and elegant - just 100 lines instead of complex event systems.
"""

import time
import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Callable
from collections import deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class Priority(Enum):
    """Notification priority levels"""
    CRITICAL = "critical"  # Show immediately (errors, failures)
    HIGH = "high"         # Show soon (warnings)
    NORMAL = "normal"     # Batch with others
    LOW = "low"           # Show when convenient


@dataclass
class Notification:
    """Simple notification message"""
    message: str
    priority: Priority
    timestamp: float
    category: str = "info"  # info, warning, error, success
    

class FlowRespectingQueue:
    """
    Notification queue that respects user flow state.
    
    Key principle: Never interrupt deep work for non-critical information.
    Batch notifications and deliver at natural break points.
    """
    
    def __init__(
        self, 
        batch_interval: int = 120,  # 2 minutes default
        max_batch_size: int = 10,
        display_callback: Optional[Callable] = None
    ):
        """
        Initialize flow-respecting notification queue.
        
        Args:
            batch_interval: Seconds between batch deliveries (default 2 min)
            max_batch_size: Maximum notifications per batch
            display_callback: Function to call with notification batch
        """
        self.batch_interval = batch_interval
        self.max_batch_size = max_batch_size
        self.display_callback = display_callback or self._default_display
        
        # Separate queues by priority
        self.critical_queue = deque()
        self.normal_queue = deque(maxlen=100)  # Limit size to prevent memory issues
        
        self.last_batch_time = time.time()
        self.notifications_held = 0
        self.in_flow_state = False
        
    def add(self, message: str, priority: Priority = Priority.NORMAL, category: str = "info"):
        """
        Add notification to queue.
        
        Critical notifications are shown immediately.
        Others are batched to respect flow state.
        """
        notification = Notification(
            message=message,
            priority=priority,
            timestamp=time.time(),
            category=category
        )
        
        if priority == Priority.CRITICAL:
            # Critical always shows immediately
            self._display_immediate(notification)
        else:
            # Queue for batching
            self.normal_queue.append(notification)
            self.notifications_held += 1
            
            # Check if we should flush
            self._maybe_flush()
    
    def _display_immediate(self, notification: Notification):
        """Display critical notification immediately"""
        logger.info(f"🚨 {notification.message}")
        if self.display_callback:
            self.display_callback([notification])
    
    def _maybe_flush(self):
        """Check if it's time to flush the queue"""
        now = time.time()
        time_since_last = now - self.last_batch_time
        
        should_flush = (
            # Time threshold reached
            time_since_last >= self.batch_interval or
            # Queue is getting full
            len(self.normal_queue) >= self.max_batch_size
        )
        
        if should_flush and not self.in_flow_state:
            self.flush()
    
    def flush(self):
        """Display all queued notifications"""
        if not self.normal_queue:
            return
            
        # Get all notifications (up to max batch size)
        batch = []
        for _ in range(min(len(self.normal_queue), self.max_batch_size)):
            if self.normal_queue:
                batch.append(self.normal_queue.popleft())
        
        if batch:
            self._display_batch(batch)
            self.last_batch_time = time.time()
            self.notifications_held = len(self.normal_queue)
    
    def _display_batch(self, notifications: List[Notification]):
        """Display a batch of notifications"""
        logger.info(f"\n{'='*50}")
        logger.info(f"📬 {len(notifications)} Notifications (batched for flow):")
        logger.info(f"{'='*50}")
        
        # Group by category for cleaner display
        by_category = {}
        for notif in notifications:
            if notif.category not in by_category:
                by_category[notif.category] = []
            by_category[notif.category].append(notif)
        
        # Display grouped notifications
        icons = {
            'info': 'ℹ️',
            'success': '✅', 
            'warning': '⚠️',
            'error': '❌'
        }
        
        for category, items in by_category.items():
            icon = icons.get(category, '📝')
            logger.info(f"\n{icon} {category.upper()}:")
            for notif in items:
                # Show age of notification
                age = int(time.time() - notif.timestamp)
                age_str = f"({age}s ago)" if age > 0 else "(now)"
                logger.info(f"  • {notif.message} {age_str}")
        
        logger.info(f"{'='*50}\n")
        
        if self.display_callback:
            self.display_callback(notifications)
    
    def _default_display(self, notifications: List[Notification]):
        """Default display callback - just log"""
        # Already logged in _display_batch
        pass
    
    def enter_flow_state(self):
        """Signal that user is in deep focus - hold all non-critical notifications"""
        self.in_flow_state = True
        logger.debug("🧘 Entering flow state - holding notifications")
    
    def exit_flow_state(self):
        """Signal that user is ready for notifications"""
        self.in_flow_state = False
        logger.debug("📬 Exiting flow state - ready for notifications")
        # Flush any pending
        if self.normal_queue:
            self.flush()
    
    def get_status(self) -> dict:
        """Get queue status"""
        return {
            'held_notifications': len(self.normal_queue),
            'in_flow_state': self.in_flow_state,
            'time_until_flush': max(0, self.batch_interval - (time.time() - self.last_batch_time)),
            'batch_interval': self.batch_interval
        }
    
    def force_flush(self):
        """Force immediate flush (for shutdown or user request)"""
        self.in_flow_state = False
        self.flush()


# Global instance for easy access
_notification_queue = FlowRespectingQueue()

def get_notification_queue() -> FlowRespectingQueue:
    """Get global notification queue instance"""
    return _notification_queue