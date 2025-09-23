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

## 🎨 Design Philosophy

### **Visual Style: Cyberpunk 2077 Inspired**
- **Dark, urban aesthetic** with neon accents
- **Glassmorphism effects** using backdrop-filter and transparency
- **High contrast** neon colors against dark backgrounds
- **Clean, minimal layout** optimized for Raspberry Pi performance

### **Color Palette**

```css
/* Professional Cyberpunk Palette */
--bg-primary: #0a0a0a;           /* Deep black background */
--bg-secondary: #1a1a1a;         /* Card backgrounds */
--bg-tertiary: #2a2a2a;          /* Elevated elements */

--accent-orange: #ff6b35;        /* Primary accent */
--accent-cyan: #00d4ff;          /* Secondary accent */
--accent-purple: #8b5cf6;        /* Tertiary accent */
--accent-yellow: #ffd60a;        /* Warning/highlight */

--text-primary: #ffffff;         /* Main text */
--text-secondary: #b3b3b3;       /* Secondary text */
--text-muted: #666666;           /* Muted text */

--glass-bg: rgba(255, 255, 255, 0.05);  /* Glassmorphism */
--glass-border: rgba(255, 255, 255, 0.1);
```

### **Typography**
- **Primary:** Inter (clean, modern sans-serif)
- **Monospace:** Space Mono (technical data display)
- **Icons:** Font Awesome 6 (scalable vector icons)

## 🏗️ Architecture

### **Frontend Stack**
- **HTML5** with semantic structure
- **CSS3** with modern features (backdrop-filter, CSS Grid, Flexbox)
- **Vanilla JavaScript** for API communication and DOM updates
- **Font Awesome 6** for iconography

### **Backend Stack**
- **Flask** (Python web framework)
- **psutil** for system monitoring
- **Session-based authentication**
- **RESTful API** for data endpoints

### **Infrastructure**
- **Cloudflare Tunnel** for secure public access
- **systemd service** for auto-startup and management
- **Shell script** for process orchestration

## 📱 Layout Design

### **Grid Structure**
```
┌─────────────────────────────────────────────────┐
│                    Header                       │
│  Sisyphus Dashboard              [Logout]       │
├─────────────────────────────────────────────────┤
│                 Status Bar                      │
│ [Host] [Disk] [RAM] [Temp] [Uptime]            │
├─────────────────────────────────────────────────┤
│              Main Content                       │
│ ┌─────────────────┐ ┌───────────┬───────────┐   │
│ │                 │ │  Docker   │    ML     │   │
│ │   CPU Cores     │ │Containers │  Models   │   │
│ │                 │ │           │           │   │
│ │  [Progress]     │ │ nginx ██  │ model1 ██ │   │
│ │  [Progress]     │ │ redis ██  │ model2 ██ │   │
│ │  [Progress]     │ │           │           │   │
│ │  [Progress]     │ │           │           │   │
│ └─────────────────┘ └───────────┴───────────┘   │
└─────────────────────────────────────────────────┘
```

### **Card Types**

#### **1. CPU Cores Card (Large Left)**
- **4 CPU core progress bars** with real-time usage
- **Font Awesome microchip icon** (`fa-microchip`)
- **Individual core monitoring** with percentage display
- **Color-coded bars** (low=green, high=red)

#### **2. Docker Containers Card (Top Right)**
- **Static container list** (nginx, redis)
- **Font Awesome Docker icon** (`fab fa-docker`)
- **Usage bars** with dummy data
- **2 rows maximum** for clean display

#### **3. ML Models Card (Bottom Right)**
- **Static model list** (model1, model2)
- **Font Awesome brain icon** (`fa-brain`)
- **Status bars** with dummy data
- **2 rows maximum** for consistency

### **Status Bar Components**
1. **Hostname** (`fa-globe`) - System identifier
2. **Disk Usage** (`fa-database`) - Storage percentage with color coding
3. **RAM Usage** (`fa-memory`) - Memory percentage with color coding
4. **Temperature** (`fa-thermometer-half`) - CPU temp with gradient colors
5. **Uptime** (`fa-clock`) - System uptime in DD:HH:MM:SS format

## 🎭 Authentication System

### **Session-Based Security**
- **Access Code:** `SuckMahBalls` (configurable in app.py)
- **Flask sessions** for state management
- **Login page** with cyberpunk styling
- **Logout functionality** with session clearing
- **Protected routes** requiring authentication

### **Login Flow**
```
1. User visits sisyphus.mohakapoor.in
2. Redirected to login page if not authenticated
3. Enter access code
4. Session token created
5. Redirected to dashboard
6. Logout clears session and redirects to login
```

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
├── scripts/
│   └── stats.py          # System monitoring
└── docs/
    └── design.md         # This documentation

startup/
├── sisyphus.sh           # Service management script
└── sisyphus.service      # systemd service file
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
- **JavaScript polling** every 2 seconds
- **Fetch API** for data retrieval
- **DOM manipulation** for UI updates
- **Error handling** for failed requests

## 🚀 Deployment & Operations

### **Cloudflare Tunnel Setup**
```bash
# Tunnel configuration in ~/.cloudflared/config.yml
tunnel: e7bfa990-8606-405a-a26e-d73bf9204dc8
credentials-file: /home/todo/.cloudflared/e7bfa990-8606-405a-a26e-d73bf9204dc8.json

ingress:
  - hostname: sisyphus.mohakapoor.in
    service: http://localhost:5000
  - service: http_status:404
```

### **systemd Service Management**
```bash
# Service control commands
sudo systemctl start sisyphus     # Start service
sudo systemctl stop sisyphus      # Stop service
sudo systemctl restart sisyphus   # Restart service
sudo systemctl status sisyphus    # Check status

# Logs and monitoring
sudo journalctl -u sisyphus -f    # Follow logs
tail -f /home/todo/logs/flask.log # Flask logs
tail -f /home/todo/logs/tunnel.log # Tunnel logs
```

### **Service Script Features**
- **Process management** with PID files
- **Graceful shutdown** handling
- **Automatic restart** on failure
- **Centralized logging** to `/home/todo/logs/`
- **Health checking** and status reporting

## 🎨 CSS Architecture

### **Glassmorphism Implementation**
```css
.card {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
```

### **Responsive Grid System**
```css
.dashboard-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 20px;
}

.cpu-card { grid-row: 1 / -1; }
.docker-card { grid-column: 2; grid-row: 1; }
.ml-card { grid-column: 2; grid-row: 2; }
```

### **Color Coding System**
- **Green (0-50%):** Safe levels
- **Yellow (50-75%):** Warning levels  
- **Red (75-100%):** Critical levels
- **Gradient transitions** for smooth visual feedback

## 🔧 Customization Guide

### **Changing Colors**
Edit CSS custom properties in `:root` selector:
```css
:root {
    --accent-orange: #your-color;
    --accent-cyan: #your-color;
    /* etc... */
}
```

### **Adding New Monitoring Cards**
1. Add HTML structure in `templates/index.html`
2. Create CSS styles in `static/styles.css`
3. Add JavaScript update logic in `static/script.js`
4. Extend API data in `app.py` if needed

### **Modifying Authentication**
Change access code in `app.py`:
```python
ACCESS_CODE = "your-new-code"
```

### **Adjusting Update Frequency**
Modify polling interval in `script.js`:
```javascript
setInterval(updateData, 2000); // 2 seconds
```

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

#### **High CPU Usage**
- **Cause:** Frequent polling or heavy operations
- **Fix:** Increase polling interval or optimize code

### **Performance Optimization**
- **Removed Chart.js** for lighter footprint
- **Minimal animations** to preserve resources
- **Efficient DOM updates** using targeted selectors
- **Static dummy data** for Docker/ML cards

## 📊 Performance Metrics

### **Target Performance (Raspberry Pi 5)**
- **CPU Usage:** < 5% average
- **RAM Usage:** < 100MB
- **Load Time:** < 2 seconds
- **Update Frequency:** 2 seconds
- **Temperature:** < 65°C optimal

### **Optimization Strategies**
- **No heavy frameworks** (jQuery, React, etc.)
- **Minimal JavaScript** with vanilla DOM manipulation
- **CSS3 hardware acceleration** for smooth effects
- **Efficient Python** with psutil for system stats

## 🔄 Future Enhancements

### **Potential Features**
- **Real Docker monitoring** via Docker API
- **Actual ML model tracking** 
- **Historical data charts** with lightweight charting
- **Custom alert thresholds**
- **Mobile responsive design**
- **Multiple theme support**
- **User management system**

### **Scalability Considerations**
- **Database integration** for historical data
- **WebSocket updates** for real-time data
- **Load balancing** for multiple Pi deployment
- **Containerization** with Docker

---

## 📝 Development Notes

**Created:** September 2025  
**Platform:** Raspberry Pi 5  
**Domain:** sisyphus.mohakapoor.in  
**Theme:** Cyberpunk 2077 inspired glassmorphism  
**Performance:** Optimized for embedded systems  

**Key Design Decisions:**
- Removed animations for Pi performance
- Static dummy data to reduce complexity
- Session-based auth for simplicity
- Glassmorphism for modern aesthetic
- Font Awesome for consistent iconography
- Vanilla JS for minimal overhead

This documentation serves as a complete reference for maintaining, customizing, and extending the Sisyphus Dashboard system.
