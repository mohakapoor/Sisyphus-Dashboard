#!/usr/bin/env python3

import psutil
import json
import time
import os
import docker

# Simple caching to reduce CPU load
_stats_cache = None
_cache_timestamp = 0
CACHE_DURATION = 2  # Cache for 2 seconds

def format_uptime(seconds):
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(days):02d}:{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def get_cpu_temp():
    # Typical location on Raspberry Pi
    temp_file = "/sys/class/thermal/thermal_zone0/temp"
    if os.path.isfile(temp_file):
        with open(temp_file) as f:
            temp_milli = int(f.read().strip())
            return round(temp_milli / 1000, 1)
    return None

def get_docker_stats():
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        running_containers = [c for c in containers if c.status == 'running']
        
        return {
            "running": len(running_containers),
            "total": len(containers)
        }
    except Exception as e:
        # If Docker is not available or there's an error, return default values
        return {"running": 0, "total": 0}


def get_stats():
    global _stats_cache, _cache_timestamp
    
    # Return cached stats if still valid
    current_time = time.time()
    if _stats_cache and (current_time - _cache_timestamp) < CACHE_DURATION:
        return _stats_cache
    
    stats = {}

    # CPU usage - reduced interval for better performance
    stats["cpu_percent_overall"] = psutil.cpu_percent(interval=0.1)
    stats["cpu_percent_per_core"] = psutil.cpu_percent(interval=0.1, percpu=True)

    # CPU temp
    temp = get_cpu_temp()
    if temp is not None:
        stats["cpu_temp_c"] = temp

    # Memory
    mem = psutil.virtual_memory()
    stats["memory_percent"] = round(mem.percent, 2)

    # Disk usage
    disk = psutil.disk_usage('/')
    stats["disk_usage"] = f"{disk.percent}%"

    # Uptime
    uptime_seconds = time.time() - psutil.boot_time()
    stats["uptime"] = format_uptime(uptime_seconds)

    # Network bytes
    net = psutil.net_io_counters()
    stats["network_bytes"] = {"rx": net.bytes_recv, "tx": net.bytes_sent}

    # Docker container stats
    docker_stats = get_docker_stats()
    stats["containers"] = docker_stats

    # Cache the results
    _stats_cache = stats
    _cache_timestamp = current_time
    
    return stats

if __name__ == "__main__":
    data = get_stats()
    print(json.dumps(data, indent=2))
