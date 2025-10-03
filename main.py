from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from sqlalchemy import text
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from database.db import engine, Base

from pathlib import Path

from todo.todo_controller import router as todos_router
from auths.auth_controller import router as auth_router
from user.user_controller import router as user_router

from todo.view.controller import router as todo_view_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Database connected")
    except Exception as e:
        print("❌ Database connection failed:", str(e))
        raise e

    # Nếu muốn tạo bảng dev mode
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield   # 👈 chỗ này nhường cho app chạy

    # --- Shutdown ---
    print("👋 Shutting down app...")

app = FastAPI(
    title="My ToDo App",
    openapi_url="/openapi.json",
    docs_url="/docs",
    description="Simple ToDo App",
    lifespan=lifespan,
)


TODO_VIEW_DIR = Path(__file__).parent / "todo" / "view"
app.mount(
    "/todo/static",
    StaticFiles(directory=str(TODO_VIEW_DIR / "static")),
    name="todo_static",
)

app.include_router(todos_router)
app.include_router(auth_router)
app.include_router(user_router)

# include router view
app.include_router(todo_view_router)