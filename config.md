# VPS Manager Development Configuration

## 1. SSH Bridge
- **Purpose**: Enables secure, password-less communication between servers for remote command execution and file transfer.
- **Configuration**:
  - **Server3**:
    - Private key: `~/.ssh/id_rsa`
  - **Server2**:
    - Hostname: `codejourney-server1`
    - Public key added to: `~/.ssh/authorized_keys`
  
## 2. OrcaOps Package
- **Purpose**: Provides tools for efficient VPS management and automation.
- **Upcoming Additions**:
  - Dockerized tools for:
    - Monitoring (e.g., Prometheus/Grafana)
    - Automated backups (e.g., Restic/Borg)
    - Container orchestration (e.g., Kubernetes, Docker Swarm)
  - Security enhancements (e.g., log monitoring, SSH auditing).

## 3. Development Roadmap
1. Finalize SSH bridge functionalities:
   - Command execution automation.
   - Logging and error handling for remote commands.
2. Dockerize tools for VPS manager:
   - Develop Docker containers for essential utilities.
   - Integrate Dockerized tools with OrcaOps APIs.
3. Extend features:
   - Add monitoring, alerting, and orchestration tools.

---
*This file is maintained to document ongoing development progress for the VPS manager and related tools.*