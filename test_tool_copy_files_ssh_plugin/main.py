from logging import debug, error, info
from pathlib import Path
from typing import Any, Callable, Dict, List

from paramiko import AutoAddPolicy, SSHClient
from stat import S_ISDIR


class CopyFilesSshCall():
    user: str
    password: str
    host: str
    local_path: Path
    remote_path: Path
    download: bool

default_copy_files_ssh_call: CopyFilesSshCall = {
    'user': '${REMOTE_CMD_USER}',
    'password': '${REMOTE_CMD_PASSWORD}',
    'host': '${REMOTE_CMD_HOST}',
    'local_path': None,
    'remote_path': None,
    'download': False
}

def run_with_ssh_client(user: str, host: str, password: str, callable: Callable[[SSHClient], None]) -> None:
    # Create an SSH client
    info(f'Connect to {user}@{host}')
    client = SSHClient()

    # Automatically add the server's host key
    client.set_missing_host_key_policy(AutoAddPolicy())

    try:
        # Connect to the remote server
        client.connect(host, username=user, password=password)

        # Run the callable
        callable(client)
    finally:
        # Close the SSH connection
        client.close()

def upload_directory(local_path: Path, remote_path: Path, sftp):
    debug(f'Upload directory {local_path.as_posix()} to {remote_path.as_posix()}')
    try:
        # Create the remote directory if it doesn't exist
        try:
            sftp.stat(remote_path.as_posix())
        except FileNotFoundError:
            sftp.mkdir(remote_path.as_posix())

        # Upload the files in the local directory
        for item in local_path.iterdir():
            if item.is_file():
                sftp.put(item.as_posix(), remote_path.joinpath(item.name).as_posix())
            elif item.is_dir():
                upload_directory(remote_path.joinpath(item.name), item, sftp)
    except FileNotFoundError:
        print(f"Local directory '{local_path}' not found.")
    except Exception as e:
        print(f"Error uploading directory: {e}")

def download_directory(remote_path: Path, local_path: Path, sftp):
    debug(f'Download directory {remote_path.as_posix()} to {local_path.as_posix()}')
    for item in sftp.listdir_attr(remote_path.as_posix()):
        remote_item = remote_path.joinpath(item.filename)
        local_item = local_path.joinpath(item.filename)

        if S_ISDIR(item.st_mode):
            local_item.mkdir(parents=True, exist_ok=True)
            download_directory(remote_item, local_item, sftp)
        else:
            sftp.get(remote_item.as_posix(), local_item.as_posix())

def copy_remote_file(client: SSHClient, local_path: Path, remote_path: Path, download: bool = False) -> None:
    # Use SFTP to copy the file
    with client.open_sftp() as sftp:
        if not download:
            info(f'Copy the file {local_path.as_posix()} to {remote_path.as_posix()}')
            # Create the remote directory if it doesn't exist
            try:
                sftp.stat(remote_path.as_posix())
            except FileNotFoundError:
                sftp.mkdir(remote_path.as_posix())

            # Copy the file
            if local_path.is_dir():
                error(f'Can not copy a directory from local to remote')
                # TODO: Test
                # upload_directory(remote_path, local_path, sftp)
                assert False
            else:
                sftp.put(local_path.as_posix(), remote_path.joinpath(local_path.name).as_posix())
        else:
            info(f'Copy the file {remote_path.as_posix()} to {local_path.as_posix()}')
            # Create the local directory if it doesn't exist
            local_path.mkdir(parents=True, exist_ok=True)

            # Copy the file
            if S_ISDIR(sftp.stat(remote_path.as_posix()).st_mode):
                download_directory(remote_path, local_path, sftp)
            else:
                sftp.get(remote_path.as_posix(), local_path.joinpath(remote_path.name).as_posix())

def make_copy_files_ssh_call(call: CopyFilesSshCall, data: Dict[str, Any]) -> None:
    # Run the cmd with client
    run_with_ssh_client(call['user'], call['host'], call['password'], lambda client: copy_remote_file(client, call["local_path"], call["remote_path"], call["download"]))

def augment_copy_files_ssh_call(call: CopyFilesSshCall, data: Dict, path: Path) -> None:
    if call['local_path'] is not None:
        call['local_path'] = Path(call['local_path'])

    if not call['local_path'].is_absolute():
        call['local_path'] = path.joinpath(call['local_path'])

    if call['remote_path'] is not None:
        call['remote_path'] = Path(call['remote_path'])
                     
def main() -> None:
    print('test-tool-copy-files-ssh-plugin')