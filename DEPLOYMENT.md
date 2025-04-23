graph TD
    A[Office Server] --> B[Docker Containers]
    B --> C[Nginx]
    B --> D[Gunicorn]
    B --> E[PostgreSQL]
    B --> F[Redis - optional]
    A --> G[UPS Backup]
    A --> H[Automated Backups]