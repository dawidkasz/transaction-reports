import uvicorn

from reports.core import models
from reports.core.database import engine
from reports.app import app  # noqa: F401


if __name__ == "__main__":
    models.Base.metadata.create_all(bind=engine)
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
