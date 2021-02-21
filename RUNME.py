import uvicorn
from server import runner as base
from server import settings

if __name__ == "__main__":
    __db_sets=settings.SETTINGS.get('db')
    if not __db_sets.get('host',False):
        exit("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\
        Configure Database in server -> settings.py\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    uvicorn.run(base.runner, log_level="debug")