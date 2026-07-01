"""Local dev entrypoint for Windows.

psycopg3's async mode cannot run on Windows' default ProactorEventLoop — only
on SelectorEventLoop. `tests/conftest.py` already switches the policy for
pytest. Running the server via the plain `uvicorn app.main:app` CLI does not:
uvicorn creates its event loop before it imports `app.main`, so a policy set
inside that module (or any module it imports) is set too late. Setting it
here, before uvicorn.run() is called, fixes it for both the plain and
--reload cases (the reload subprocess re-executes this module's top-level
code too, since it sits outside the __main__ guard).
"""
import asyncio
import sys

import uvicorn

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
