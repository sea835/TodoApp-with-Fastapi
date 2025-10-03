import sys
import os
import importlib
import pkgutil
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Đường dẫn project (lấy folder cha của migrations/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

# Import Base từ core
from core.basemodel import Base
from database.db import engine

# Cấu hình logger của alembic.ini
config = context.config
fileConfig(config.config_file_name)

# ---- Tự động import tất cả model trong modules/ ----
import modules

def import_all_models():
    for _, modname, _ in pkgutil.walk_packages(modules.__path__, modules.__name__ + "."):
        if modname.endswith("_model"):
            importlib.import_module(modname)

import_all_models()

# Đây là metadata để Alembic autogenerate schema
target_metadata = Base.metadata

# ---- Run migrations ----
def run_migrations_offline():
    """Chạy migration ở chế độ offline (xuất SQL script)."""
    url = str(engine.url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Chạy migration ở chế độ online (kết nối DB thật)."""
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
