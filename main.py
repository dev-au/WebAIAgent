import asyncio
import sys
from agent.loop import agent_loop


async def main():
    if len(sys.argv) > 1:
        user_request = " ".join(sys.argv[1:])
    else:
        print("Enter your request for the web agent:")
        user_request = input("> ")

    if not user_request:
        print("No request provided. Exiting.")
        return

    await agent_loop(user_request)


if __name__ == "__main__":
    asyncio.run(main())
