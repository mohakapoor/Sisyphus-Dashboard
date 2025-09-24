let cpuCoresInitialized = false;

async function fetchStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();

        // Update status badges
        updateStatusBadges(data);

        // Initialize CPU cores progress bars if not done
        if (!cpuCoresInitialized) {
            initializeCpuCores(data.cpu_percent_per_core.length);
            cpuCoresInitialized = true;
        }

        // Update CPU cores
        updateCpuCores(data.cpu_percent_per_core, data.cpu_percent_overall);

        // Update all stat displays
        updateStats(data);
        
        // Docker and ML models are now static - no updates needed

    } catch (err) {
        console.error('Error fetching stats:', err);
    }
}

function initializeCpuCores(numCores) {
    const container = document.getElementById('cpuCoresList');
    container.innerHTML = '';
    
    for (let i = 0; i < numCores; i++) {
        const coreElement = document.createElement('div');
        coreElement.className = 'stat-item';
        coreElement.innerHTML = `
            <div class="stat-label">
                <span>Core ${i}</span>
                <span class="stat-value" id="core${i}Percent">--%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill progress-cpu" id="core${i}Progress" style="width: 0%"></div>
            </div>
        `;
        container.appendChild(coreElement);
    }
}

function updateCpuCores(cpuValues, overallCpu) {
    // Update overall CPU
    document.getElementById('cpuOverall').textContent = `${overallCpu.toFixed(1)}% Overall`;
    
    // Update each core
    cpuValues.forEach((value, index) => {
        const percentElement = document.getElementById(`core${index}Percent`);
        const progressElement = document.getElementById(`core${index}Progress`);
        
        if (percentElement && progressElement) {
            percentElement.textContent = `${value.toFixed(1)}%`;
            progressElement.style.width = `${value}%`;
        }
    });
}

function updateStats(data) {
    // These stats are now handled in the status bar, so this function can be simplified
    // or used for other system stats if needed
}

// Docker and ML model functions removed - now using static data in HTML

function updateStatusBadges(data) {
    // Update disk usage in status bar
    const diskDisplay = document.getElementById('diskDisplay');
    if (data.disk_usage !== undefined) {
        const diskUsed = parseInt(data.disk_usage);
        diskDisplay.textContent = `Disk: ${diskUsed}%`;
        
        // Color coding for disk usage
        const diskBadge = document.getElementById('diskBadge');
        if (diskUsed > 85) {
            diskBadge.style.borderColor = '#ef4444'; // Red
        } else if (diskUsed > 70) {
            diskBadge.style.borderColor = '#f59e0b'; // Yellow
        } else {
            diskBadge.style.borderColor = 'rgba(255, 255, 255, 0.1)'; // Default
        }
    }
    
    // Update memory usage in status bar
    const memDisplay = document.getElementById('memDisplay');
    if (data.memory_percent !== undefined) {
        memDisplay.textContent = `RAM: ${data.memory_percent.toFixed(1)}%`;
        
        // Color coding for memory usage
        const memBadge = document.getElementById('memBadge');
        if (data.memory_percent > 80) {
            memBadge.style.borderColor = '#ef4444'; // Red
        } else if (data.memory_percent > 60) {
            memBadge.style.borderColor = '#f59e0b'; // Yellow
        } else {
            memBadge.style.borderColor = 'rgba(255, 255, 255, 0.1)'; // Default
        }
    }
    
    // Update temperature badge
    const tempDisplay = document.getElementById('tempDisplay');
    const tempBadge = document.getElementById('tempBadge');
    
    if (data.cpu_temp_c) {
        tempDisplay.textContent = `${data.cpu_temp_c}°C`;
        
        // Color coding for temperature
        if (data.cpu_temp_c > 75) {
            tempBadge.style.borderColor = '#ef4444'; // Red
        } else if (data.cpu_temp_c > 60) {
            tempBadge.style.borderColor = '#f59e0b'; // Yellow
        } else {
            tempBadge.style.borderColor = 'rgba(255, 255, 255, 0.1)'; // Default
        }
    }
    
    // Update uptime badge
    const uptimeDisplay = document.getElementById('uptimeDisplay');
    
    if (data.uptime) {
        // Use the same format as the main card (DD:HH:MM:SS)
        uptimeDisplay.textContent = data.uptime;
    }
}

// Check user role and show admin features
async function checkUserRole() {
    try {
        const response = await fetch('/api/stats');
        if (response.ok) {
            // If we can access stats, check if admin features should be shown
            // We'll determine this by trying to access an admin endpoint
            const adminResponse = await fetch('/api/admin/shutdown', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            // If admin endpoint doesn't return 403, user is admin
            if (adminResponse.status !== 403) {
                document.getElementById('shutdownBtn').style.display = 'inline-flex';
            }
        }
    } catch (error) {
        console.log('Role check failed:', error);
    }
}

// Shutdown function (admin only)
function confirmShutdown() {
    if (confirm('⚠️ WARNING: This will shutdown the Raspberry Pi!\n\nAre you absolutely sure?')) {
        if (confirm('🚨 FINAL CONFIRMATION: Shutdown Pi5 now?')) {
            // Require re-authentication
            const adminCode = prompt('🔐 SECURITY: Enter admin code to confirm shutdown:');
            if (adminCode) {
                shutdownPi(adminCode);
            }
        }
    }
}

async function shutdownPi(adminCode) {
    try {
        const response = await fetch('/api/admin/shutdown', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                admin_code: adminCode
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('🔴 Pi is shutting down securely...\nConnection will be lost shortly.');
            // Redirect after alert
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else {
            alert('❌ Shutdown failed: ' + data.error);
        }
    } catch (error) {
        alert('❌ Shutdown request failed: ' + error.message);
    }
}

// Logout function
function logout() {
    // Show confirmation
    if (confirm('Are you sure you want to logout?')) {
        // Redirect to logout route
        window.location.href = '/logout';
    }
}

// Initial fetch and update every 3 seconds (lighter on Pi)
fetchStats();
checkUserRole(); // Check if user is admin and show shutdown button
setInterval(fetchStats, 3000);
