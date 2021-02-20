import uvicorn
from server import runner as base


if __name__ == "__main__":
    uvicorn.run(base.backend, log_level="debug")