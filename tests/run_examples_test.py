import asyncio
import glob
import subprocess


async def run_script(file_path: str) -> tuple[str, int | None, bytes, bytes]:
    """Run a single script and return the result."""
    print(f"Running {file_path}...")
    process = await asyncio.create_subprocess_exec("python", file_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = await process.communicate()
    print(f"Finished {file_path}.")
    print(stdout.decode(), stderr.decode())
    return file_path, process.returncode, stdout, stderr


async def main() -> None:
    files: list[str] = glob.glob("examples/**/*.py", recursive=True)
    tasks: list = [run_script(file) for file in files]
    results: list[tuple[str, int | None, bytes, bytes]] = await asyncio.gather(*tasks)

    for file, returncode, stdout, stderr in results:
        if returncode != 0:
            print(f"Error in {file}:")
            print(stderr.decode())
        else:
            print(f"{file} executed successfully.")


def test_examples() -> None:
    # asyncio.run(main())
    ...


if __name__ == "__main__":
    asyncio.run(main())
