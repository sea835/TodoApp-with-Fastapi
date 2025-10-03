import sys
import os
from alembic.config import Config
from alembic import command

alembic_cfg = Config("alembic.ini")

def make_migration(msg: str):
    command.revision(alembic_cfg, message=msg, autogenerate=True)

def upgrade(target="head"):
    command.upgrade(alembic_cfg, target)

def downgrade(target="-1"):
    command.downgrade(alembic_cfg, target)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: migrate.py [make|upgrade|downgrade] [message_or_target]")
        sys.exit(1)

    action = sys.argv[1]
    if action == "make":
        msg = sys.argv[2] if len(sys.argv) > 2 else "new migration"
        make_migration(msg)
    elif action == "upgrade":
        target = sys.argv[2] if len(sys.argv) > 2 else "head"
        upgrade(target)
    elif action == "downgrade":
        target = sys.argv[2] if len(sys.argv) > 2 else "-1"
        downgrade(target)
    else:
        print("Unknown command")
