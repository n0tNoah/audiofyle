import uvicorn
from server import runner as base


if __name__ == "__main__":
    uvicorn.run(base.runner, log_level="debug")