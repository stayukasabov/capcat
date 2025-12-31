# Deployment Guide

Production deployment guide for Capcat's hybrid architecture system.

## Deployment Overview

Capcat supports multiple deployment scenarios from development environments to production-scale news archiving systems.

## Deployment Architecture

```
Production Deployment Options
├── Single Server Deployment (Recommended)
│   ├── Application server with hybrid architecture
│   ├── Local file storage for archives
│   └── Cron-based scheduling
└── Distributed Deployment (Advanced)
    ├── Multiple worker nodes
    ├── Shared network storage
    └── Load balancing and coordination
```

## Pre-Deployment Checklist

### System Requirements
- **Python**: 3.8+ (recommended: 3.11+)
- **Memory**: Minimum 2GB RAM (recommended: 4GB+)
- **Storage**: 50GB+ available space for archives
- **Network**: Stable internet connection
- **CPU**: 2+ cores (recommended: 4+ cores)

### Dependency Verification
```bash
# Check Python version
python3 --version

# Verify pip and venv
python3 -m pip --version
python3 -m venv --help

# Check system utilities
which curl
which git
```

## Single Server Deployment

### 1. Environment Setup

```bash
# Create deployment directory
sudo mkdir -p /opt/capcat
sudo chown $USER:$USER /opt/capcat
cd /opt/capcat

# Clone application (or copy files)
git clone https://your-repo/capcat.git .
# OR: Copy application files to /opt/capcat

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "from core.source_system.source_registry import get_source_registry; print(f'{len(get_source_registry().get_available_sources())} sources')"
```

### 2. Production Configuration

Create production configuration file:

```yaml
# /opt/capcat/config/production.yml
network:
  connect_timeout: 15
  read_timeout: 10
  user_agent: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
  max_retries: 3
  retry_delay: 2.0

processing:
  max_workers: 8
  download_images: true
  download_videos: false  # Disable to save bandwidth/storage
  download_audio: false
  download_documents: false
  skip_existing: true

logging:
  default_level: "INFO"
  use_colors: false
  log_to_file: true
  log_file_path: "/var/log/capcat/capcat.log"
  max_file_size: "50MB"
  backup_count: 5
  format: "detailed"

output:
  base_path: "/data/capcat/archives"
  date_format: "%d-%m-%Y"
  create_date_folders: true
  sanitize_filenames: true
```

### 3. Directory Structure Setup

```bash
# Create necessary directories
sudo mkdir -p /data/capcat/archives
sudo mkdir -p /var/log/capcat
sudo mkdir -p /etc/capcat

# Set permissions
sudo chown -R $USER:$USER /data/capcat
sudo chown -R $USER:$USER /var/log/capcat

# Copy configuration
cp config/production.yml /etc/capcat/capcat.yml

# Set environment variable
echo 'export CAPCAT_CONFIG_FILE="/etc/capcat/capcat.yml"' >> ~/.bashrc
source ~/.bashrc
```

### 4. Service Configuration

Create systemd service for automated operation:

```bash
# Create service file
sudo tee /etc/systemd/system/capcat.service << 'EOF'
[Unit]
Description=Capcat News Archiving Service
After=network.target

[Service]
Type=oneshot
User=capcat
Group=capcat
WorkingDirectory=/opt/capcat
Environment=CAPCAT_CONFIG_FILE=/etc/capcat/capcat.yml
ExecStart=/opt/capcat/venv/bin/python /opt/capcat/capcat.py bundle all --count 20
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create timer for regular execution
sudo tee /etc/systemd/system/capcat.timer << 'EOF'
[Unit]
Description=Run Capcat every 6 hours
Requires=capcat.service

[Timer]
OnCalendar=*-*-* 00,06,12,18:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Enable and start timer
sudo systemctl daemon-reload
sudo systemctl enable capcat.timer
sudo systemctl start capcat.timer
```

### 5. Monitoring Setup

Create monitoring script:

```bash
# Create monitoring script
tee /opt/capcat/monitor.py << 'EOF'
#!/usr/bin/env python3
"""Capcat monitoring script."""

import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

def check_recent_archives(hours=24):
    """Check for recent archive creation."""
    archive_path = Path("/data/capcat/archives")
    cutoff_time = datetime.now() - timedelta(hours=hours)

    recent_files = []
    for file_path in archive_path.rglob("*.md"):
        if datetime.fromtimestamp(file_path.stat().st_mtime) > cutoff_time:
            recent_files.append(file_path)

    return len(recent_files)

def check_service_status():
    """Check systemd service status."""
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "capcat.timer"],
            capture_output=True, text=True
        )
        return result.stdout.strip() == "active"
    except:
        return False

def check_disk_space():
    """Check available disk space."""
    try:
        result = subprocess.run(
            ["df", "-h", "/data/capcat"],
            capture_output=True, text=True
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            fields = lines[1].split()
            return fields[4]  # Usage percentage
    except:
        return "Unknown"

def generate_status_report():
    """Generate system status report."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "recent_archives": check_recent_archives(),
        "service_active": check_service_status(),
        "disk_usage": check_disk_space(),
        "system": "operational" if check_recent_archives() > 0 and check_service_status() else "issue"
    }

    return report

if __name__ == "__main__":
    status = generate_status_report()
    print(json.dumps(status, indent=2))

    # Write status to file
    with open("/var/log/capcat/status.json", "w") as f:
        json.dump(status, f, indent=2)
EOF

chmod +x /opt/capcat/monitor.py

# Add monitoring to cron
(crontab -l 2>/dev/null; echo "*/30 * * * * /opt/capcat/monitor.py") | crontab -
```

## Advanced Deployment Options

### 1. Kubernetes Deployment

```yaml
# k8s-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: capcat
  labels:
    app: capcat
spec:
  replicas: 1
  selector:
    matchLabels:
      app: capcat
  template:
    metadata:
      labels:
        app: capcat
    spec:
      containers:
      - name: capcat
        image: capcat:latest
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        volumeMounts:
        - name: data-volume
          mountPath: /data
        - name: config-volume
          mountPath: /app/config
        env:
        - name: CAPCAT_CONFIG_FILE
          value: "/app/config/k8s.yml"
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: capcat-data-pvc
      - name: config-volume
        configMap:
          name: capcat-config

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: capcat-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi

---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: capcat-cron
spec:
  schedule: "0 */6 * * *"  # Every 6 hours
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: capcat
            image: capcat:latest
            command: ["python", "capcat.py", "bundle", "all", "--count", "20"]
            volumeMounts:
            - name: data-volume
              mountPath: /data
          volumes:
          - name: data-volume
            persistentVolumeClaim:
              claimName: capcat-data-pvc
          restartPolicy: OnFailure
```

### 2. Load Balancing Setup

```bash
# nginx load balancer configuration
# /etc/nginx/sites-available/capcat
upstream capcat {
    server 10.0.1.10:8080;
    server 10.0.1.11:8080;
    server 10.0.1.12:8080;
}

server {
    listen 80;
    server_name capcat.example.com;

    location / {
        proxy_pass http://capcat;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

## Production Monitoring

### 1. Performance Monitoring

```python
# performance_monitor.py
import psutil
import time
import json
from pathlib import Path

class ProductionMonitor:
    def __init__(self):
        self.metrics = {}

    def collect_system_metrics(self):
        """Collect system performance metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/data/capcat').percent,
            "network_io": psutil.net_io_counters()._asdict(),
            "process_count": len(psutil.pids())
        }

    def collect_application_metrics(self):
        """Collect application-specific metrics."""
        from core.source_system.performance_monitor import get_performance_monitor

        monitor = get_performance_monitor()
        all_metrics = monitor.get_all_metrics()

        return {
            "total_sources": len(all_metrics),
            "avg_success_rate": sum(m.success_rate for m in all_metrics.values()) / len(all_metrics),
            "total_requests": sum(m.total_requests for m in all_metrics.values()),
            "avg_response_time": sum(m.avg_response_time for m in all_metrics.values()) / len(all_metrics)
        }

    def generate_report(self):
        """Generate comprehensive monitoring report."""
        return {
            "timestamp": time.time(),
            "system": self.collect_system_metrics(),
            "application": self.collect_application_metrics()
        }

if __name__ == "__main__":
    monitor = ProductionMonitor()
    report = monitor.generate_report()

    # Write to monitoring file
    with open('/var/log/capcat/metrics.json', 'w') as f:
        json.dump(report, f, indent=2)
```

### 2. Log Aggregation

```bash
# Setup log rotation
sudo tee /etc/logrotate.d/capcat << 'EOF'
/var/log/capcat/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 capcat capcat
    postrotate
        systemctl reload capcat || true
    endscript
}
EOF
```

### 3. Alerting Setup

```python
# alerting.py
import smtplib
import json
from email.mime.text import MimeText
from datetime import datetime, timedelta

class AlertManager:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def check_alerts(self):
        """Check for alert conditions."""
        alerts = []

        # Check recent activity
        with open('/var/log/capcat/status.json', 'r') as f:
            status = json.load(f)

        if status['recent_archives'] == 0:
            alerts.append("No recent archives created in last 24 hours")

        if not status['service_active']:
            alerts.append("Capcat service is not active")

        disk_usage = int(status['disk_usage'].rstrip('%'))
        if disk_usage > 90:
            alerts.append(f"Disk usage critical: {disk_usage}%")

        return alerts

    def send_alert(self, alerts, recipient):
        """Send alert email."""
        if not alerts:
            return

        subject = f"Capcat Alert - {len(alerts)} issues detected"
        body = f"""
Capcat Alert Report
Generated: {datetime.now()}

Issues detected:
{chr(10).join(f"- {alert}" for alert in alerts)}

Please check the system status and logs.
        """

        msg = MimeText(body)
        msg['Subject'] = subject
        msg['From'] = self.username
        msg['To'] = recipient

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)

if __name__ == "__main__":
    alerter = AlertManager(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        username="alerts@example.com",
        password="password"
    )

    alerts = alerter.check_alerts()
    if alerts:
        alerter.send_alert(alerts, "admin@example.com")
```

## Security Considerations

### 1. User Permissions

```bash
# Create dedicated user
sudo useradd -r -s /bin/false -d /opt/capcat capcat

# Set proper permissions
sudo chown -R capcat:capcat /opt/capcat
sudo chown -R capcat:capcat /data/capcat
sudo chown -R capcat:capcat /var/log/capcat

# Restrict access
chmod 750 /opt/capcat
chmod 750 /data/capcat
```

### 2. Firewall Configuration

```bash
# UFW firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. SSL/TLS Configuration

```bash
# Let's Encrypt SSL certificate
sudo apt install certbot
sudo certbot --nginx -d capcat.example.com
```

## Deployment Checklist

### Pre-Deployment
- [ ] System requirements verified
- [ ] Dependencies installed
- [ ] Configuration files created
- [ ] Directory structure setup
- [ ] Permissions configured
- [ ] Security measures implemented

### Deployment
- [ ] Application deployed
- [ ] Service configured and started
- [ ] Monitoring setup
- [ ] Logging configured
- [ ] Backups configured
- [ ] Health checks implemented

### Post-Deployment
- [ ] Functional testing completed
- [ ] Performance testing completed
- [ ] Monitoring alerts configured
- [ ] Documentation updated
- [ ] Team training completed
- [ ] Maintenance procedures documented

## Maintenance Procedures

### 1. Regular Updates

```bash
# Update application
cd /opt/capcat
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart capcat
```

### 2. Backup Procedures

```bash
# Backup script
#!/bin/bash
BACKUP_DIR="/backup/capcat/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup configuration
cp -r /etc/capcat "$BACKUP_DIR/"

# Backup recent archives (last 30 days)
find /data/capcat/archives -mtime -30 -type f | tar czf "$BACKUP_DIR/recent_archives.tar.gz" -T -

# Backup logs
cp -r /var/log/capcat "$BACKUP_DIR/"

echo "Backup completed: $BACKUP_DIR"
```

### 3. Health Checks

```bash
# Health check script
#!/bin/bash
set -e

echo "Checking Capcat health..."

# Check service status
systemctl is-active --quiet capcat.timer || { echo "Timer not active"; exit 1; }

# Check recent archives
RECENT_COUNT=$(find /data/capcat/archives -mtime -1 -name "*.md" | wc -l)
if [ "$RECENT_COUNT" -eq 0 ]; then
    echo "No recent archives"
    exit 1
fi

# Check disk space
DISK_USAGE=$(df /data/capcat | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "Disk usage critical: ${DISK_USAGE}%"
    exit 1
fi

echo "All health checks passed"
```

---

*This deployment guide provides comprehensive procedures for production deployment of Capcat across multiple environments and scales.*