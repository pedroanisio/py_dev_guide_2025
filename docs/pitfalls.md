## 13. Edge‑Case Pitfalls & Gotchas  🛑  
| Category     | Gotcha                                               | Mitigation                                                |
| ------------ | ---------------------------------------------------- | --------------------------------------------------------- |
| **asyncio**  | Blocking lib in `async def` freezes loop.            | Use `asyncio.to_thread` or process pool.                  |
|              | `asyncio.run()` inside running loop (e.g., Jupyter). | Use `await` or `nest_asyncio`.                            |
| **Docker**   | Memory‑overcommit OOM kills containers.              | Set `mem_limit`, monitor `docker stats`.                  |
|              | Mac OS file‑sync slowness.                           | Mount volumes with `cached` or use *colima*.              |
| **Gunicorn** | Worker timeout kills long streaming responses.       | Switch to `uvicorn --reload` in dev or tweak `--timeout`. |
| **Celery**   | Lost tasks when broker restarts.                     | Enable `acks_late` + `worker_prefetch_multiplier=1`.      |  
---