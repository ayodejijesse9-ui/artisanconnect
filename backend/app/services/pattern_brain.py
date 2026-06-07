# ============================================
# ArtisanConnect Nigeria — pattern_brain.py
# ============================================

from collections import Counter
import time

# Global in-memory data store for pattern recognition
SYSTEM_EVENT_LOGS = []

def record_system_event(event_type: str, actor: str, metadata: str):
    """
    Logs an event with a timestamp to build a behavioral history.
    """
    SYSTEM_EVENT_LOGS.append({
        "timestamp": time.time(),
        "event_type": event_type,  # 'failed_auth', 'bio_update', 'booking'
        "actor": actor,            # IP address, User ID, or Artisan ID
        "metadata": metadata       # Extra text context
    })

def analyze_patterns() -> dict:
    """
    Scans historical event logs to recognize structural anomalies or optimization trends.
    """
    now = time.time()
    # Filter logs from the last 10 minutes for real-time analysis
    recent_logs = [log for log in SYSTEM_EVENT_LOGS if now - log["timestamp"] < 600]
    
    # 1. Detect Auth Attack Patterns
    failed_auth_actors = [log["actor"] for log in recent_logs if log["event_type"] == "failed_auth"]
    auth_counts = Counter(failed_auth_actors)
    suspicious_ips = [ip for ip, count in auth_counts.items() if count >= 3]
    
    # 2. Detect Optimization Quality Patterns
    short_bios_count = sum(1 for log in recent_logs if log["event_type"] == "bio_update" and len(log["metadata"]) < 30)
    
    return {
        "active_threat_level": "HIGH" if suspicious_ips else "LOW",
        "suspicious_actors": suspicious_ips,
        "formatting_trend": "CRITICAL_SHORTAGE_OF_DETAILED_BIOS" if short_bios_count >= 2 else "OPTIMAL"
    }