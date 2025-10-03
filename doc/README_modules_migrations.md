# Hướng dẫn sử dụng generate_module.py và migrate.py

## 1. generate_module.py

Script `generate_module.py` dùng để tạo hoặc xoá **module** mới trong thư mục `modules`.

### Cách dùng

```bash
# Tạo module 'todo' kèm view
python generate_module.py todo -view=true

# Tạo module 'todo' không kèm view
python generate_module.py todo -view=false

# Xoá module 'todo'
python generate_module.py todo delete
```

### Cấu trúc sinh ra

Ví dụ khi tạo `todo -view=true`, project sẽ có cấu trúc:

```
modules/
  todo/
    __init__.py
    todo_model.py
    todo_schema.py
    todo_service.py
    todo_controller.py
    view/
      __init__.py
      controller.py
      static/
        style.css
      templates/
        index.html
        detail.html
        form.html
```

- **Model**: kế thừa `BaseModel`, định nghĩa bảng.
- **Schema**: định nghĩa các lớp Create/Update/Out cho Pydantic.
- **Service**: kết nối `CoreService` với model.
- **Controller**: tạo router CRUD chuẩn hoá theo `CoreController`.
- **View** (nếu có): Jinja2 template render cho module.

Ngoài ra, script sẽ **tự động import và include router** trong `main.py`.

---

## 2. migrate.py

Script `migrate.py` dùng để quản lý migrations với Alembic.

### Cách dùng

```bash
# Tạo file migration mới với message
python migrate.py make "create todo table"

# Nâng DB lên migration mới nhất
python migrate.py upgrade head

# Quay lại migration trước đó
python migrate.py downgrade -1

# Đánh dấu DB ở trạng thái hiện tại
python migrate.py stamp head
```

### Cấu trúc thư mục migrations

```
migrations/
  versions/
    <timestamp>_<message>.py   # các file migration sinh ra
  env.py                       # cấu hình Alembic (điểm vào)
  script.py.mako               # template mặc định
  alembic.ini                  # file config Alembic (nếu có)
```

- `env.py` định nghĩa `target_metadata` lấy từ `Base.metadata` (toàn bộ models).
- Các file trong `versions/` ghi lại lịch sử thay đổi schema DB.

---

## 3. Quy trình phát triển

1. Thêm/sửa model trong `modules/..._model.py`
2. Chạy `python migrate.py make "message"` để tạo migration
3. Chạy `python migrate.py upgrade head` để apply
4. Commit code kèm migration

---

## 4. Ghi chú

- **Không chỉnh sửa tay DB schema** → mọi thay đổi phải thông qua model + migration.
- Có thể rollback bằng `downgrade` khi cần.

