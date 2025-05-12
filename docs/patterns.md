## 5. Essential Design Patterns for Modern Python Applications 

Design patterns are proven, reusable solutions to recurring design problems. In Python, we can often implement them more concisely than in Java/C++ thanks to first‑class functions, descriptors, `dataclasses`, and dynamic typing. This section captures the patterns you will meet most often when building **service‑oriented**, **async**, and **typed** Python codebases today.

> **Convention** – Code examples assume **Python 3.12+** with `pyproject.toml`‑driven builds, [PEP 561](https://peps.python.org/pep-0561/) type stubs, `ruff`, and `mypy --strict`. Replace `your_pkg` with the real package name.

---

### 5.1 Creational Patterns

#### 5.1.1 Factory Method
*Decouple object creation from usage; swap implementations via config/DI.*

```python
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    async def write(self, key: str, data: bytes) -> None: ...

class S3Storage(Storage):
    async def write(self, key: str, data: bytes) -> None:
        # uses aioboto3
        pass

class FSStorage(Storage):
    async def write(self, key: str, data: bytes) -> None:
        # filesystem implementation
        pass

def make_storage(kind: str) -> Storage:
    return {
        "s3": S3Storage(),
        "fs": FSStorage(),
    }[kind]
```

#### 5.1.2 Abstract Factory
*Group related factories; enforce product families.*

```python
from abc import ABC
from typing import Protocol

class UserDAO(Protocol):
    async def find_by_id(self, user_id: int): ...

class OrderDAO(Protocol):
    async def find_by_user(self, user_id: int): ...

class DAOFactory(ABC):
    user: UserDAO
    order: OrderDAO

class PostgresDAOFactory(DAOFactory):
    user = PgUserDAO()
    order = PgOrderDAO()

DAO: DAOFactory = PostgresDAOFactory()
```

#### 5.1.3 Builder
*Build complex objects step‑by‑step with fluent API.*

```python
from dataclasses import dataclass, field

@dataclass
class Query:
    selects: list[str]
    where: list[str] = field(default_factory=list)

class QueryBuilder:
    def __init__(self):
        self._q = Query([])

    def select(self, *cols: str):
        self._q.selects.extend(cols); return self
    def where(self, cond: str):
        self._q.where.append(cond); return self
    def build(self) -> Query: return self._q

q = QueryBuilder().select("id", "name").where("age > 18").build()
```

#### 5.1.4 Singleton (Registry)
*One global instance (e.g., config). Use module‑level constants or DI instead of classic class‑based singleton.*

```python
# config.py
import tomllib, pathlib
from functools import cache

@cache
def config() -> dict:
    """Load config lazily and cache result"""
    return tomllib.loads(pathlib.Path("pyproject.toml").read_text())
```

#### 5.1.5 Dependency Container
*Centralized service/resource management with type safety*

```python
from typing import Annotated, get_type_hints

class Container:
    def __init__(self):
        self._services = {}
        
    def register(self, service_type: type, instance: object) -> None:
        self._services[service_type] = instance
        
    def resolve(self, service_type: type) -> object:
        return self._services.get(service_type)

# Usage with type annotations
container = Container()
container.register(Database, PostgresDB())

def get_user(db: Annotated[Database, Inject]):
    # Injected at runtime
    pass
```

---
### 5.2 Structural Patterns

#### 5.2.1 Adapter (a.k.a. Wrapper)
*Smoothly plug incompatible APIs together; prefer `typing.Protocol` for zero‑cost adaptation.*

```python
from typing import Protocol

class Notifier(Protocol):
    async def send(self, msg: str) -> None: ...

class SlackClient:
    async def post_message(self, text: str): ...

class SlackAdapter:
    def __init__(self, client: SlackClient): self._c = client
    async def send(self, msg: str): await self._c.post_message(text=msg)
```

#### 5.2.2 Facade

*Expose a thin, convenient API over a complex subsystem.*

```python
class PaymentsFacade:
    def __init__(self, gateway: Gateway, ledger: Ledger):
        self.gateway, self.ledger = gateway, ledger
    async def charge(self, user: User, amount: Money):
        tx = await self.gateway.charge(user, amount)
        await self.ledger.record(tx)
        return tx.receipt_url
```

#### 5.2.3 Decorator (runtime behavior augmentation)

```python
from functools import wraps
from time import perf_counter
import logging

logger = logging.getLogger(__name__)

def timed(fn):
    @wraps(fn)
    async def inner(*a, **kw):
        start = perf_counter(); res = await fn(*a, **kw)
        logger.info("%s took %.2f ms", fn.__name__, (perf_counter()-start)*1e3)
        return res
    return inner
```

#### 5.2.4 Proxy

*Delay heavy initialisation, add caching, or enforce permissions.*

```python
class LazyDB:
    def __init__(self, url: str):
        self._url, self._db = url, None
    async def _ensure(self):
        if self._db is None:
            self._db = await connect(self._url)
    async def query(self, q: str):
        await self._ensure(); return await self._db.query(q)
```

#### 5.2.5 Composite

*Create tree structures where individual components and composites share the same interface.*

```python
from abc import ABC, abstractmethod
from typing import List

class Component(ABC):
    @abstractmethod
    async def execute(self) -> None: ...

class Task(Component):
    async def execute(self) -> None:
        # Do the actual work
        pass

class TaskGroup(Component):
    def __init__(self) -> None:
        self._children: List[Component] = []
        
    def add(self, component: Component) -> None:
        self._children.append(component)
        
    async def execute(self) -> None:
        for child in self._children:
            await child.execute()
```

---

### 5.3 Behavioral Patterns

#### 5.3.1 Strategy
*Pass algorithms as first‑class callables or plug via DI.*

```python
from typing import Callable, TypeAlias

Sorter: TypeAlias = Callable[[list[int]], list[int]]

def bubble(xs: list[int]) -> list[int]: 
    # Implementation details
    return sorted(xs)

def quick(xs: list[int]) -> list[int]:
    # Implementation details 
    return sorted(xs)

def do_sort(xs: list[int], strategy: Sorter = sorted):
    return strategy(xs)
```

#### 5.3.2 Command
*Encapsulate user request or task for queuing/undo.*

```python
from dataclasses import dataclass
from typing import Protocol

class EmailSvc(Protocol):
    async def send(self, to: str, subject: str, body: str) -> None: ...

@dataclass
class EmailCommand:
    to: str; subject: str; body: str
    async def execute(self, svc: EmailSvc):
        await svc.send(self.to, self.subject, self.body)
```

#### 5.3.3 Observer (Pub/Sub)
*Async event stream via `asyncio.Queue`.*

```python
import asyncio
from typing import List, TypeVar, Generic

T = TypeVar('T')

class EventBus(Generic[T]):
    def __init__(self):
        self.subscribers: List[asyncio.Queue[T]] = []
        
    async def publish(self, msg: T):
        for q in self.subscribers:
            await q.put(msg)
            
    async def subscribe(self) -> asyncio.Queue[T]:
        q: asyncio.Queue[T] = asyncio.Queue()
        self.subscribers.append(q)
        return q
```

#### 5.3.4 Template Method
*Define skeleton algorithm in base class.*

```python
from abc import ABC, abstractmethod
from typing import Any

class ETLPipeline(ABC):
    def run(self):
        data = self.extract()
        data = self.transform(data)
        self.load(data)
        
    @abstractmethod
    def extract(self) -> Any: ...
    
    def transform(self, d: Any) -> Any:
        return d  # override optionally
        
    @abstractmethod
    def load(self, d: Any) -> None: ...
```

#### 5.3.5 State
*Model finite‑state workflows; transition via composition not giant `if` chains.*

```python
from typing import Protocol

class ArticleState(Protocol):
    def publish(self, article: "Article") -> None: ...
    def can_edit(self) -> bool: ...

class Draft:
    def publish(self, article: "Article") -> None:
        article.state = Published()
    def can_edit(self) -> bool:
        return True

class Published:
    def publish(self, article: "Article") -> None:
        pass  # Already published
    def can_edit(self) -> bool:
        return False

class Article:
    def __init__(self):
        self.state: ArticleState = Draft()
        
    def publish(self):
        self.state.publish(self)
        
    def can_edit(self) -> bool:
        return self.state.can_edit()
```

#### 5.3.6 Chain of Responsibility
*Pass requests through a chain of handlers.*

```python
from typing import Optional, Protocol, cast
from abc import ABC, abstractmethod

class Request:
    def __init__(self, data: dict): 
        self.data = data

class Handler(Protocol):
    def set_next(self, handler: "Handler") -> "Handler": ...
    def handle(self, request: Request) -> Optional[str]: ...

class AbstractHandler(ABC):
    _next: Optional["Handler"] = None
    
    def set_next(self, handler: Handler) -> Handler:
        self._next = handler
        return handler
        
    def handle(self, request: Request) -> Optional[str]:
        if self._next:
            return self._next.handle(request)
        return None
        
class AuthHandler(AbstractHandler):
    def handle(self, request: Request) -> Optional[str]:
        if not request.data.get("token"):
            return "Unauthorized"
        return super().handle(request)
```

---
### 5.4 Architectural & Domain Patterns

*These patterns shape higher‑level module boundaries and data flow.*

#### 5.4.1 Dependency Injection
*Swap collaborators in tests; avoid global state.*

```python
from typing import Protocol, Type, TypeVar, cast, get_type_hints

T = TypeVar('T')

class ServiceLocator:
    _services = {}
    
    @classmethod
    def register(cls, protocol: Type[T], implementation: T) -> None:
        cls._services[protocol] = implementation
    
    @classmethod
    def resolve(cls, protocol: Type[T]) -> T:
        return cast(T, cls._services.get(protocol))
```

#### 5.4.2 Repository
*Abstract persistence; unit tests hit in‑mem repos.*

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

class UserRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id: int) -> Optional[User]: ...
    
    @abstractmethod
    async def save(self, user: User) -> User: ...

class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self.users: dict[int, User] = {}
        
    async def find_by_id(self, id: int) -> Optional[User]:
        return self.users.get(id)
        
    async def save(self, user: User) -> User:
        self.users[user.id] = user
        return user
```

#### 5.4.3 Unit of Work
*Batch DB work into atomic commit/rollback.*

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator

class UnitOfWork:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        
    @asynccontextmanager
    async def __call__(self) -> AsyncGenerator["ActiveUoW", None]:
        session = self.session_factory()
        active = ActiveUoW(session)
        try:
            yield active
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

class ActiveUoW:
    def __init__(self, session):
        self.session = session
        # Repositories using this session
        self.users = UserRepository(session)
        self.orders = OrderRepository(session)
```

#### 5.4.4 CQRS
*Separate read models from write commands.*

```python
from pydantic import BaseModel
from typing import List

# Command
class CreateUserCommand(BaseModel):
    name: str
    email: str
    
async def handle_create_user(cmd: CreateUserCommand, uow: UnitOfWork):
    async with uow() as txn:
        user = User(name=cmd.name, email=cmd.email)
        await txn.users.save(user)
        await event_bus.publish("user_created", user.id)

# Query (read model)
class UserDTO(BaseModel):
    id: int
    name: str
    
async def get_users() -> List[UserDTO]:
    # Optimized for reads, possibly from a cache or read replica
    return [UserDTO(id=1, name="Alice")]
```

#### 5.4.5 Event Sourcing
*Persist state changes as a sequence of events*

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

class Event(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any]
    
class EventStore:
    async def append(self, stream_id: str, event: Event) -> None: ...
    async def get_events(self, stream_id: str) -> List[Event]: ...
    
class Aggregate:
    def __init__(self, id: str, events: List[Event]):
        self.id = id
        self._changes: List[Event] = []
        # Apply all historical events
        for event in events:
            self._apply(event)
            
    def get_changes(self) -> List[Event]:
        return self._changes
        
    def _apply(self, event: Event) -> None:
        # Apply the event to update state
        handler = getattr(self, f"apply_{event.type}")
        handler(event.data)
        
    def _record(self, type: str, data: Dict[str, Any]) -> None:
        # Record a new event
        event = Event(type=type, data=data)
        self._apply(event)
        self._changes.append(event)
```

---
### 5.5 Concurrency Patterns

#### 5.5.1 Producer ↔ Consumer (`asyncio.Queue`)
```python
import asyncio
import aiofiles
from pathlib import Path
from typing import Optional

async def producer(path: Path, queue: asyncio.Queue[Optional[bytes]]):
    async with aiofiles.open(path, "rb") as f:
        while chunk := await f.read(1024):
            await queue.put(chunk)
    await queue.put(None)  # sentinel

async def consumer(queue: asyncio.Queue[Optional[bytes]], storage: Storage):
    chunk_id = 0
    while (chunk := await queue.get()) is not None:
        await storage.write(f"chunk_{chunk_id}", chunk)
        chunk_id += 1
        queue.task_done()
```

#### 5.5.2 Fan‑out / Fan‑in with `TaskGroup` (≥ 3.11)

```python
import asyncio
from typing import List

async def fetch(url: str) -> bytes:
    # Implementation details
    return b"response data"

async def gather_urls(urls: List[str]) -> List[bytes]:
    results = []
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch(url)) for url in urls]
    return [task.result() for task in tasks]
```

#### 5.5.3 Background Task Manager

```python
import asyncio
from typing import Dict, Callable, Awaitable, Any, Optional
from uuid import UUID, uuid4

class BackgroundTaskManager:
    def __init__(self):
        self._tasks: Dict[UUID, asyncio.Task] = {}
        
    async def start(self, coro: Awaitable[Any]) -> UUID:
        task_id = uuid4()
        task = asyncio.create_task(self._run_and_cleanup(task_id, coro))
        self._tasks[task_id] = task
        return task_id
        
    async def _run_and_cleanup(self, task_id: UUID, coro: Awaitable[Any]):
        try:
            return await coro
        finally:
            self._tasks.pop(task_id, None)
            
    def cancel(self, task_id: UUID) -> bool:
        task = self._tasks.get(task_id)
        if task:
            task.cancel()
            return True
        return False
        
    async def wait_for(self, task_id: UUID) -> Optional[Any]:
        task = self._tasks.get(task_id)
        if task:
            return await task
        return None
```

#### 5.5.4 Circuit Breaker

```python
import asyncio
from enum import Enum, auto
from typing import Callable, TypeVar, Awaitable, Optional, cast
from datetime import datetime, timedelta

T = TypeVar('T')

class CircuitState(Enum):
    CLOSED = auto()      # Normal operation
    OPEN = auto()        # Circuit is broken, fail fast
    HALF_OPEN = auto()   # Testing if service is back

class CircuitBreaker:
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: timedelta = timedelta(seconds=30),
                 timeout: float = 10.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.timeout = timeout
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time: Optional[datetime] = None
        
    async def call(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        if self.state == CircuitState.OPEN:
            if (datetime.now() - cast(datetime, self.last_failure_time)) > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is open")
                
        try:
            result = await asyncio.wait_for(func(*args, **kwargs), timeout=self.timeout)
            
            if self.state == CircuitState.HALF_OPEN:
                self.failures = 0
                self.state = CircuitState.CLOSED
                
            return result
            
        except Exception as e:
            self.failures += 1
            self.last_failure_time = datetime.now()
            
            if self.failures >= self.failure_threshold or self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                
            raise e
```

---

### 5.6 Checklist: Pattern Selection Guidelines

1. **Validate the smell first** – patterns solve *specific* pain points (tight coupling, redundancy, brittle tests).
2. **Prefer composition over inheritance** – increase flexibility.
3. **Stay Pythonic** – leverage protocols, dataclasses, generators before heavier OO.
4. **Write tests for each variation** – patterns without safety nets breed complexity.
5. **Document the intent** – link to this file in code comments (`docs/patterns.md#section-5-2-1`).
6. **Start simple** – only introduce patterns when the complexity justifies it.
7. **Use type hints** – they make patterns more explicit and help with refactoring.

---

#### Further Reading

* γ Addison, *Architecture Patterns with Python* (O'Reilly, 2020)
* G. van Rossum, *PEP 557 – Data Classes*
* E. Gamma et al., *Design Patterns* (Addison‑Wesley, 1994) – still relevant but adapt syntax.
* A. Beaulieu, *Learning SQL (3rd Edition)* (O'Reilly, 2020)
* R. Martinsen, *Domain-Driven Design in Python* (2023)
