## 9. API Development — FastAPI **(Mandatory)**  🚀  
### Why FastAPI?  
* First‑class **async** support (built on Starlette).
* **OpenAPI** docs auto‑generated → contract‑driven dev.
* Pydantic integration = zero‑boilerplate validation.  
### Quick‑start Skeleton  
```python
# app/main.py ★ HDR required in actual project files
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel

class Health(BaseModel):
status: str = "ok"

app = FastAPI(title="My API", version="1.0.0")

@app.get("/health", response_model=Health, tags=["meta"])
async def health() -> Health:
return Health()

# Auth dependency
async def get_current_user(token: str = Depends(oauth2_scheme)):
user = verify_token(token)
if not user:
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
return user

@app.get("/secure")
async def secure_endpoint(user = Depends(get_current_user)):
return {"user": user}
```  
### Production Guidelines  
| Concern       | Mandate                                                                  |
| ------------- | ------------------------------------------------------------------------ |
| Workers       | **uvicorn\[standard]** via Gunicorn (`-k uvicorn.workers.UvicornWorker`) |
| Timeouts      | 60 s hard, 30 s read.                                                    |
| CORS          | Restrict origins in `CORSMiddleware`.                                    |
| Rate Limiting | Deploy Traefik plugin or Redis‑based SlowAPI.                            |  
---