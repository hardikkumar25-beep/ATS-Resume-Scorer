from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from config.constants import WORK_DIRECTORY,TIMEOUT

def getDocker():
    docker=DockerCommandLineCodeExecutor(
        work_dir=WORK_DIRECTORY,
        timeout=TIMEOUT
    )
    return docker

async def startDocker(docker):
    print("Starting Docker Executor...")
    await docker.start()
    print("Docker Executor started.")

async def stopDocker(docker):
    print("Stopping Docker Executor...")
    await docker.stop()
    print("Docker Executor stopped.")