# Sisyphus Dashboard - Design Documentation

## 🚀 Quick Service Management Commands

```bash
# Service Control
sudo systemctl start sisyphus     # Start service
sudo systemctl stop sisyphus      # Stop service
sudo systemctl restart sisyphus   # Restart service
sudo systemctl status sisyphus    # Check status

# Logs and Monitoring
sudo journalctl -u sisyphus -f    # Follow real-time logs
tail -f /home/todo/logs/flask.log # Flask application logs
tail -f /home/todo/logs/tunnel.log # Cloudflare tunnel logs

# System Health
vcgencmd measure_temp             # Check Pi temperature
free -h                           # Memory usage
df -h                            # Disk usage
uptime                           # System uptime
```

## 🎯 Project Overview

**Sisyphus Dashboard** is a cyberpunk-themed, glassmorphism-styled monitoring dashboard for Raspberry Pi 5. It provides real-time system statistics, Docker container monitoring, and ML model tracking through a modern web interface accessible globally via Cloudflare Tunnel.



## 🛠️ Technical Implementation

### **File Structure**
```
HomeApi/
├── app.py                 # Flask application & routes
├── static/
│   ├── styles.css        # All CSS styling
│   └── script.js         # Frontend JavaScript
├── templates/
│   ├── index.html        # Main dashboard
│   └── login.html        # Authentication page
└── readme.md             # This documentation

scripts/
└── stats.py              # System monitoring (outside HomeApi)

startup/
├── sisyphus.sh           # Service management script  
└── sisyphus.service      # systemd service file

logs/
├── flask.log             # Flask application logs
└── tunnel.log            # Cloudflare tunnel logs
```

### **API Endpoints**
- `GET /` - Root redirect logic
- `GET /login` - Authentication page
- `POST /authenticate` - Login processing
- `GET /dashboard` - Main dashboard (protected)
- `GET /logout` - Session termination
- `GET /api/stats` - System data API (protected)
- `GET /static/<file>` - Static file serving

### **Real-time Updates**
- **JavaScript polling** every 3 seconds
- **Fetch API** for data retrieval
- **DOM manipulation** for UI updates
- **Error handling** for failed requests

## 🚨 Troubleshooting

### **Common Issues**

#### **CSS Not Loading on Tunnel**
- **Cause:** Static file routing
- **Fix:** Explicit static route in Flask app

#### **Authentication Not Working**
- **Cause:** Session configuration
- **Fix:** Ensure `app.secret_key` is set

#### **Service Won't Start**
- **Cause:** File permissions or paths
- **Fix:** Check executable permissions and file paths

## 🔄 Future Enhancements


### **Scalability Considerations**
- **Database integration** for historical data
- **WebSocket updates** for real-time data
- **Load balancing** for multiple Pi deployment
- **Containerization** with Docker

---
