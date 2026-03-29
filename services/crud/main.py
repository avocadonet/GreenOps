import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))


async def main():
    from uvicorn import run

    run("infrastructure.server:app", reload=True, port=5000, host="0.0.0.0")


if __name__ == "__main__":
    asyncio.run(main())
