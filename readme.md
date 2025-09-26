# Sisyphus Dashboard - Design Documentation

## 🚀 Quick Service Management Commands

```bash
# Docker Container Management
cd /home/todo/docker/sisyphus
docker-compose up --build -d     # Build and start containers
docker-compose down              # Stop containers
docker-compose restart          # Restart containers
docker-compose logs -f          # Follow container logs

# Cloudflare Tunnel Service
sudo systemctl status cloudflared    # Check tunnel status
sudo journalctl -u cloudflared -f    # Follow tunnel logs

# System Health
vcgencmd measure_temp             # Check Pi temperature
free -h                           # Memory usage
df -h                            # Disk usage
uptime                           # System uptime
docker ps                        # Running containers
```

## 🎯 Project Overview

**Sisyphus Dashboard** is a containerized monitoring dashboard for Raspberry Pi 5. It provides real-time system statistics, live Docker container monitoring, and network activity tracking through a modern web interface accessible globally via Cloudflare Tunnel.

### **Key Features**
- 🖥️ **Real-time System Stats**: CPU, memory, disk, temperature monitoring
- 🐳 **Live Container Stats**: Running and total container counts
- 🌐 **Network Monitoring**: Upload/download bandwidth tracking  
- 🔗 **Portainer Integration**: Direct link to container management
- 🔐 **Secure Access**: Session-based authentication with role management
- ☁️ **Global Access**: Cloudflare Tunnel with custom domain



## 🛠️ Technical Implementation

### **Architecture**
- **Frontend**: Responsive web interface with real-time updates
- **Backend**: Flask API with system monitoring and Docker integration
- **Containerization**: Docker Compose for service orchestration
- **Networking**: Cloudflare Tunnel for secure external access
- **Authentication**: Session-based with configurable access levels

### **File Structure**
```
HomeApi/
├── app.py                 # Flask application & routes
├── stats.py               # System & Docker monitoring
├── static/
│   ├── styles-v3.css     # Modern CSS styling
│   └── script-v3.js      # Frontend JavaScript with live updates
├── templates/
│   ├── index.html        # Main dashboard
│   └── login.html        # Authentication page
└── readme.md             # This documentation

docker/sisyphus/
├── docker-compose.yml    # Container orchestration
├── Dockerfile            # Container build instructions
└── requirements.txt      # Python dependencies

.cloudflared/
└── sisyphus-config.yml   # Tunnel configuration (domains routing)
```

### **API Endpoints**
- `GET /` - Root redirect logic
- `GET /login` - Authentication page  
- `POST /authenticate` - Login processing
- `GET /dashboard` - Main dashboard (protected)
- `GET /logout` - Session termination
- `GET /api/stats` - System & container data API (protected)
- `GET /api/docs` - API documentation
- `POST /api/admin/shutdown` - Pi shutdown (admin only)
- `GET /static/<file>` - Static file serving

### **Real-time Updates**
- **JavaScript polling** every 3 seconds for live data
- **System metrics**: CPU cores, memory, disk, temperature
- **Container stats**: Running/total container counts via Docker API
- **Network activity**: Upload/download bandwidth tracking
- **Error handling** with graceful fallbacks

### **Environment Variables**
Required variables in `/home/todo/HomeApi/.env`:
```bash
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Authentication (NO DEFAULTS - must be set)
VIEWER_ACCESS_CODE=your-viewer-code
ADMIN_ACCESS_CODE=your-admin-code

# Domain Configuration
MAIN_DOMAIN=your-main-domain.com
PORTAINER_DOMAIN=your-portainer-domain.com
```

## 🚨 Troubleshooting

### **Common Issues**

#### **Container Won't Start**
- **Cause:** Build errors or port conflicts
- **Fix:** Check logs with `docker-compose logs` and ensure port 5000 is free

#### **Container Stats Not Showing**
- **Cause:** Docker socket not mounted or permissions
- **Fix:** Ensure `/var/run/docker.sock` is mounted in docker-compose.yml

#### **Static Files Not Loading**
- **Cause:** Cache issues or incorrect paths
- **Fix:** Hard refresh browser or rebuild container with `--no-cache`

#### **Authentication Issues**
- **Cause:** Missing environment variables
- **Fix:** Verify `.env` file exists with all required variables (see Environment Variables section)

#### **Domain Configuration Issues**
- **Cause:** Missing domain environment variables
- **Fix:** Set `MAIN_DOMAIN` and `PORTAINER_DOMAIN` in `.env` file

## 🔄 Future Enhancements

### **Potential Improvements**
- **Historical data storage** with lightweight database
- **WebSocket integration** for instant updates (currently 3s polling)
- **Container resource monitoring** (CPU/memory per container)
- **Alert system** for resource thresholds
- **Multiple Pi deployment** with centralized monitoring

### **Security Notes**
- **Environment variables**: All sensitive data stored in `.env` (never committed)
- **Docker socket exposure**: Limited to read-only container information
- **Session management**: Regenerated secrets and single admin sessions
- **Tunnel security**: Cloudflare handles TLS termination and DDoS protection

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
