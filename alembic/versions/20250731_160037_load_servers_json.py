from alembic import op
import sqlalchemy as sa
import json
from uuid import uuid4

revision = "20250731_160037"
down_revision = "20250731_160024"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    with open('servers.json') as f:
        data = json.load(f)
    for name, cfg in data.items():
        if name == 'server1':
            continue
        conn.execute(
            sa.text(
                "INSERT INTO servers (id, hostname, provider, public_ip, role, status, tags) "
                "VALUES (:id, :hostname, 'LOCAL', :public_ip, 'dev', 'online', '{}')"
            ),
            {
                'id': str(uuid4()),
                'hostname': cfg['hostname'],
                'public_ip': cfg['hostname']
            }
        )

def downgrade():
    pass
