import asyncio
from backend.main import process_collection_download, collection_tasks
import time

task_id = "test-task-123"
process_collection_download(task_id, "album", "189843871")
print(collection_tasks[task_id])
