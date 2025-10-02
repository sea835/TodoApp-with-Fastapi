from core.core_controller import CoreController
from core.core_service import CoreService
from todo.todo_model import TodoModel
from todo.todo_schema import TodoCreate, TodoUpdate, TodoOut

todo_service = CoreService(TodoModel)

todo_controller = CoreController(
    service=todo_service,
    create_schema=TodoCreate,
    update_schema=TodoUpdate,
    out_schema=TodoOut,
    prefix="/todo",
    tag="Todos",
    search_fields=["name", "description"]  # hỗ trợ /todo/search?q=...
)

router = todo_controller.router