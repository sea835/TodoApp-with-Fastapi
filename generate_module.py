import os
import sys
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent
MAIN_FILE = BASE_DIR / "main.py"
MODULES_DIR = BASE_DIR / "modules"

MODEL_TEMPLATE = """\
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from core.basemodel import BaseModel

class {ModelName}Model(BaseModel):
    __tablename__ = '{module}'
    {module}_id = Column(Integer, primary_key=True)
    # Add your fields here
"""

SCHEMA_TEMPLATE = """\
import datetime as dt
from core.core_schema import CoreSchema, CoreCreateSchema, CoreUpdateSchema

class {ModelName}Create(CoreCreateSchema):
    pass

class {ModelName}Update(CoreUpdateSchema):
    pass

class {ModelName}Out(CoreSchema[int]):
    pass
"""

SERVICE_TEMPLATE = """\
from modules.{module}.{module}_model import {ModelName}Model
from core.core_service import CoreService

{module}_service = CoreService({ModelName}Model)
"""

CONTROLLER_TEMPLATE = """\
from core.core_controller import CoreController
from core.core_service import CoreService
from modules.{module}.{module}_model import {ModelName}Model
from modules.{module}.{module}_schema import {ModelName}Create, {ModelName}Update, {ModelName}Out

{module}_service = CoreService({ModelName}Model)

{module}_controller = CoreController(
    service={module}_service,
    create_schema={ModelName}Create,
    update_schema={ModelName}Update,
    out_schema={ModelName}Out,
    prefix="/{module}",
    tag="{ModelName}s",
    search_fields=[],
)

router = {module}_controller.router
"""

VIEW_CONTROLLER_TEMPLATE = '''\
from pathlib import Path
from fastapi import APIRouter, Request
from starlette.templating import Jinja2Templates
from starlette.responses import HTMLResponse

router = APIRouter(prefix="/{module}/view", tags=["{ModelName} Views"])

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {{"request": request}})
'''

HTML_INDEX = """<!DOCTYPE html>
<html>
<head><title>{ModelName} Index</title></head>
<body><h1>{ModelName} Index</h1></body>
</html>
"""

HTML_DETAIL = """<!DOCTYPE html>
<html>
<head><title>{ModelName} Detail</title></head>
<body><h1>{ModelName} Detail</h1></body>
</html>
"""

HTML_FORM = """<!DOCTYPE html>
<html>
<head><title>{ModelName} Form</title></head>
<body><h1>{ModelName} Form</h1></body>
</html>
"""

def ensure_modules_dir():
    MODULES_DIR.mkdir(exist_ok=True)
    init_file = MODULES_DIR / "__init__.py"
    if not init_file.exists():
        init_file.write_text("")

def create_module(module_name: str, with_view: bool):
    ensure_modules_dir()

    model_name = module_name.capitalize()
    module_dir = MODULES_DIR / module_name
    module_dir.mkdir(exist_ok=True)

    # __init__.py cho module
    (module_dir / "__init__.py").write_text("")

    # Core files
    (module_dir / f"{module_name}_model.py").write_text(MODEL_TEMPLATE.format(ModelName=model_name, module=module_name))
    (module_dir / f"{module_name}_schema.py").write_text(SCHEMA_TEMPLATE.format(ModelName=model_name, module=module_name))
    (module_dir / f"{module_name}_service.py").write_text(SERVICE_TEMPLATE.format(ModelName=model_name, module=module_name))
    (module_dir / f"{module_name}_controller.py").write_text(CONTROLLER_TEMPLATE.format(ModelName=model_name, module=module_name))

    # Views
    if with_view:
        view_dir = module_dir / "view"
        static_dir = view_dir / "static"
        templates_dir = view_dir / "templates"

        static_dir.mkdir(parents=True, exist_ok=True)
        templates_dir.mkdir(parents=True, exist_ok=True)

        # __init__.py trong view
        (view_dir / "__init__.py").write_text("")

        (view_dir / "controller.py").write_text(VIEW_CONTROLLER_TEMPLATE.format(ModelName=model_name, module=module_name))
        (templates_dir / "index.html").write_text(HTML_INDEX.format(ModelName=model_name))
        (templates_dir / "detail.html").write_text(HTML_DETAIL.format(ModelName=model_name))
        (templates_dir / "form.html").write_text(HTML_FORM.format(ModelName=model_name))
        (static_dir / "style.css").write_text("body { font-family: sans-serif; }")

    # Update main.py (import + include router)
    import_lines = []
    include_lines = []

    import_lines.append(f"from modules.{module_name}.{module_name}_controller import router as {module_name}_router\n")
    include_lines.append(f"app.include_router({module_name}_router)\n")

    if with_view:
        import_lines.append(f"from modules.{module_name}.view.controller import router as {module_name}_view_router\n")
        include_lines.append(f"app.include_router({module_name}_view_router)\n")

    with open(MAIN_FILE, "r+", encoding="utf-8") as f:
        content = f.read()
        imports_to_add = "".join(l for l in import_lines if l not in content)
        includes_to_add = "".join(l for l in include_lines if l not in content)

        # đặt import lên đầu file
        if imports_to_add:
            content = imports_to_add + content
        # thêm include xuống cuối file
        if includes_to_add:
            if not content.endswith("\n"):
                content += "\n"
            content += "\n" + includes_to_add

        f.seek(0)
        f.write(content)
        f.truncate()

def delete_module(module_name: str):
    module_dir = MODULES_DIR / module_name
    if module_dir.exists():
        shutil.rmtree(module_dir)
        print(f"🗑️  Deleted module folder: {module_dir}")

    # Xóa import và include trong main.py
    if MAIN_FILE.exists():
        content = MAIN_FILE.read_text(encoding="utf-8")

        import_lines = [
            f"from modules.{module_name}.{module_name}_controller import router as {module_name}_router\n",
            f"from modules.{module_name}.view.controller import router as {module_name}_view_router\n",
        ]
        include_lines = [
            f"app.include_router({module_name}_router)\n",
            f"app.include_router({module_name}_view_router)\n",
        ]

        for line in import_lines + include_lines:
            content = content.replace(line, "")

        MAIN_FILE.write_text(content, encoding="utf-8")
        print(f"🗑️  Removed imports and routers for '{module_name}' from main.py")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python generate_module.py <module_name> -view=true/false")
        print("  python generate_module.py <module_name> delete")
        sys.exit(1)

    module_name = sys.argv[1].lower()
    action = sys.argv[2].lower()

    if action.startswith("-view="):
        with_view = action == "-view=true"
        create_module(module_name, with_view)
        print(f"✅ Module '{module_name}' created in 'modules/' with view={with_view}")
    elif action == "delete":
        delete_module(module_name)
        print(f"✅ Module '{module_name}' deleted from 'modules/'")
    else:
        print("❌ Unknown action:", action)
