import asyncio

from daytona_sdk import Daytona, DaytonaConfig, SessionExecuteRequest


async def main():
    config = DaytonaConfig(
        api_key="dtn_27573ca37b2bcefc0e3398be68d4dc381f326f3299aa183df6572a8a10144bd1",
        server_url="https://stage.daytona.work/api",
        target="eu",
    )

    daytona = Daytona(config)
    sandbox = daytona.create()

    try:
        session_id = "my-session"
        sandbox.process.create_session(session_id)

        _ = sandbox.process.execute_session_command(
            session_id,
            SessionExecuteRequest(
                # command="echo 'Hello, World!'",
                command='counter=1; while (( counter <= 3 )); do echo "Count: $counter"; ((counter++)); sleep 2; done',
                var_async=True,
            ),
        )
        # print(f"cmd_response: {cmd_response}")

        session = sandbox.process.get_session(session_id)
        # print(f"session commands: {session.commands}")

        # execute_session_command returns None if var_async is True, for some reason,
        # so we need to get the command id from the session
        cmd_id = session.commands[0].id

        # Stream logs concurrently using asyncio.create_task
        logs_task = asyncio.create_task(
            sandbox.process.get_session_command_logs_stream(session_id, cmd_id, lambda x: print(f"=== chunk: {x}"))
        )

        print("Continuing execution while logs are streaming...")
        await asyncio.sleep(2)
        print("Other operations completed!")

        print("Now waiting for logs to complete...")
        await logs_task
    finally:
        print("Cleaning up sandbox...")
        daytona.remove(sandbox)


if __name__ == "__main__":
    asyncio.run(main())
