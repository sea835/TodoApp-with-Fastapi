from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import text
from starlette.staticfiles import StaticFiles

from database.db import engine

from pathlib import Path

from modules.todo.todo_controller import router as todos_router
from modules.auths.auth_controller import router as auth_router
from modules.user.user_controller import router as user_router

from modules.todo.view.controller import router as todo_view_router

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


TODO_VIEW_DIR = Path(__file__).parent / "modules" / "todo" / "view"
app.mount(
    "/modules/todo/static",
    StaticFiles(directory=str(TODO_VIEW_DIR / "static")),
    name="todo_static",
)

app.include_router(todos_router)
app.include_router(auth_router)
app.include_router(user_router)

# include router view
app.include_router(todo_view_router)