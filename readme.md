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

**Sisyphus Dashboard** is a monitoring dashboard for Raspberry Pi 5 hosted on it. It provides real-time system statistics, Docker container monitoring, and ML model tracking through a modern web interface accessible globally via Cloudflare Tunnel.



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

## ⚠️ CRITICAL LESSONS LEARNED - CACHING NIGHTMARE

### What Went Wrong
1. **Over-optimization**: Added aggressive 1-year caching headers (`max-age=31536000`) without any real need
2. **Cloudflare Stubbornness**: CDN cached files with these headers and refused to serve updates
3. **Development Hell**: Spent hours fighting cache instead of building features
4. **Cache-busting Failures**: Multiple attempts with timestamps, headers, and restarts failed

### The Problem Timeline
1. ✅ Built working dashboard
2. ❌ Added "production optimizations" (1-year caching)
3. ❌ Cloudflare cached everything aggressively  
4. ✅ Made code changes (shutdown button functionality)
5. ❌ Tunnel served old cached files, local worked fine
6. ❌ Tried 10+ "solutions" that didn't work
7. ✅ Finally: renamed files (`script-v2.js`, `styles-v2.css`) to bypass cache entirely

### Root Cause
```python
# THE MISTAKE:
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year cache - STUPID!

# THE FIX:
# Nothing - let Flask handle it normally with sensible defaults
```

### How To Never Deal With This Again

#### 1. NEVER Add Aggressive Caching Without Need
```python
# DON'T DO THIS:
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year

# DO THIS INSTEAD:
# Nothing - Flask defaults are fine for small projects
```

#### 2. Use Anti-Cache Headers During Development
```python
@app.after_request
def no_cache_during_dev(response):
    if app.debug:  # Only during development
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache' 
        response.headers['Expires'] = '0'
    return response
```

#### 3. Smart Development Workflow
```bash
# Always test locally first
curl http://localhost:5000/static/script.js

# Then test tunnel
curl https://your-tunnel.com/static/script.js

# Compare content-length and last-modified dates to detect cache issues
```

#### 4. Version Static Files From Day 1 (If You Must Cache)
```html
<!-- Instead of: -->
<script src="/static/script.js"></script>

<!-- Do this: -->
<script src="/static/script.v{{ app_version }}.js"></script>
```

#### 5. Environment-Specific Configs
```python
if os.getenv('ENVIRONMENT') == 'production':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600  # 1 hour max
else:
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # No caching for dev
```

#### 6. Cloudflare Management (If You Control Domain)
- **Development Mode**: Temporarily bypasses caching
- **Purge Cache**: Manual cache clearing when needed
- **Cache Rules**: Granular control over what gets cached

### The Golden Rule
**KEEP IT SIMPLE UNTIL YOU ACTUALLY NEED OPTIMIZATION!**

Don't add "production optimizations" to solve problems you don't have. A simple Raspberry Pi dashboard doesn't need aggressive caching - it needs to work reliably and update when you change code.

### Emergency Cache-Busting Techniques
If you ever get stuck in cache hell again:

1. **Rename files** (most effective): `script.js` → `script-v2.js`
2. **Change URLs** with timestamps: `script.js?v=123456789`
3. **Add cache-control headers**: `Cache-Control: no-cache, no-store, must-revalidate`
4. **Cloudflare purge** (if you have access)
5. **Use different domain/subdomain** for testing

Remember: **The user never asked for caching optimizations** - they just wanted a working dashboard!

---
