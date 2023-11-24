# universal-test-tool

[![codecov](https://codecov.io/gh/jackovsky8/universal-test-tool/branch/main/graph/badge.svg?token=universal-test-tool_token_here)](https://codecov.io/gh/jackovsky8/universal-test-tool)
[![CI](https://github.com/jackovsky8/universal-test-tool/actions/workflows/main.yml/badge.svg)](https://github.com/jackovsky8/universal-test-tool/actions/workflows/main.yml)

Awesome universal-test-tool to make tests configurable with a yaml file.

## Install the repository
```bash
pip install universal-test-tool
```

## Run the tests

```bash
test-tool

# This programm is a tool for running tests.

# options:
#   -h, --help            show this help message and exit
#   -p PROJECT, --project PROJECT
#                         The path to the project.
#   -ca CALLS, --calls CALLS
#                         The filename of the calls configuration.
#   -d DATA, --data DATA  The filename of the data configuration.
#   -X, --debug           Activate debugging.
```

### Calls File
Per default a file ```calls.yaml``` is searched in the project folder, which is by default the current working directory.

It is a list where every entry is one step to test.

The tests are done in the following available plugins:
- Bash Cmd (test_tool_bash_cmd_plugin)
- Copy Files SSH (test_tool_copy_files_ssh_plugin)
- JDBC SQL (test_tool_jdbc_sql_plugin)
- Rest (test_tool_rest_plugin)
- SSH Cmd (test_tool_ssh_cmd_plugin)

#### Bash Cmd (test_tool_bash_cmd_plugin)
Runs a command on the local machine.

##### Call:
```yaml
- type: BASH_CMD
    call:
        cmd: None
        timeout: None
        save: None
```


Object for save:
```yaml
save:
    name: None
    type: None
```

##### Parameters:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   cmd   |   None   |   The command to run.   |
|   timeout   |   None   |   The timeout for the command.   |
|   save   |   None   |   Save the result to value.   |


Parameters for save:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   name   |   None   |   The name for the variable to save the result in.   |
|   type   |   None   |   The type for how to treat the result (STRING, JSON).   |

#### Copy Files SSH (test_tool_copy_files_ssh_plugin)
Copies files and folders between local machine and remote machine via ssh.

##### Call:
```yaml
- type: COPY_FILES_SSH
    call:
        user: ${REMOTE_CMD_USER}
        password: ${REMOTE_CMD_PASSWORD}
        host: ${REMOTE_CMD_HOST}
        local_path: None
        remote_path: None
        download: False
```
##### Parameters:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   user   |   ${REMOTE_CMD_USER}   |   The user for the ssh connection.   |
|   password   |   ${REMOTE_CMD_PASSWORD}   |   The password for the ssh connection.   |
|   host   |   ${REMOTE_CMD_HOST}   |   The host for the ssh connection.   |
|   local_path   |   None   |   The local file or folder for the transfer.   |
|   remote_path   |   None   |   The remote file or folder for the transfer.   |
|   download   |   False   |   If this flag is set to true, the file transfer is a download, otherwise it is an upload.   |

#### JDBC SQL (test_tool_jdbc_sql_plugin)
Runs SQL Statements with [JayDeBeApi](https://pypi.org/project/JayDeBeApi/).

##### Call:
```yaml
- type: JDBC_SQL
    call:
    query: None,
    save: [],
    validate: [],
    driver: ${DB_DRIVER},
    driver_path: ${DB_DRIVER_PATH},
    url: ${DB_URL},
    username: ${DB_USERNAME},
    password: ${DB_PASSWORD}
```
Object for save:
```yaml
save:
    raw: None
    column: None
    name: None
```
Object for validate:
```yaml
save:
    raw: None
    column: None
    value: None
```
##### Parameters:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   query   |   None   |   The SQL statement to run   |
|   save   |   []   |   Save a entry of a cell to a variable   |
|   vaidate   |   []   |   Validate the entry of a cell   |
|   driver   |   ${DB_DRIVER}   |   The Class of the driver   |
|   driver_path   |   ${DB_DRIVER_PATH}   |   The Path of the jar file   |
|   url   |   ${DB_URL}   |   The jdbc connection string   |
|   username   |   ${DB_USERNAME}   |   The username of the db   |
|   password   |   ${DB_PASSWORD}   |   The password of the db   |

#### Rest (test_tool_rest_plugin)
Tests REST endpoints.

##### Call:
```yaml
- type: REST
    call:
        base_url: ${REST_BASE_URL}
        path: ${REST_PATH}
        url: None
        method: GET
        data: None
        files: None
        payload: None
        headers: {}
        response_type: JSON
        assertion: None
        hide_logs: False
        status_codes: [200]
```
##### Parameters:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   base_url   |   ${REST_BASE_URL}   |   The base url of the service to test.   |
|   path   |   ${REST_PATH}   |   The path of the endpoint to test.   |
|   url   |  None   |   The url value is built dynamically from ${base_url}/${path} if not set. Otherwiese the oder values are ignored.   |
|   method   |   GET   |   The method of the call. (GET, POST, DELETE, PUT)   |
|   data   |   None   |   The data of the http call, an object is used as json.   |
|   files   |   None   |   Path of files to send.   |
|   payload   |   None   |   Payload for multipart request.   |
|   header   |   {}   |   Headers to use for request.   |
|   response_type   |  JSON   |   How to pasrse the response. (JSON, XML, TEXT)   |
|   assertion   |   NONE   |   The assertion how the response should look like   |
|   hide_log   |   False   |   Don't print the reply in the logs.   |
|   status_codes   |   [200]   |   The status codes to accept.   |

#### SSH Cmd (test_tool_ssh_cmd_plugin)
Runs a command on a remote machine via ssh.

##### Call:
```yaml
- type: SSH_CMD
    call:
        user: ${REMOTE_CMD_USER}
        password: ${REMOTE_CMD_PASSWORD}
        host: ${REMOTE_CMD_HOST}
        cmd: None
```
##### Parameters:
| Parameter | Default | Description |
|:---------:|:--------:|:--------:|
|   user   |   ${REMOTE_CMD_USER}   |   The user for the ssh connection.   |
|   password   |   ${REMOTE_CMD_PASSWORD}   |   The password for the ssh connection.   |
|   host   |   ${REMOTE_CMD_HOST}   |   The host for the ssh connection.   |
|   cmd   |   None   |   The command to run.   |

#### Other available plugins:

This project can handle other plugins as well. There just need to be a installed module with the name test_tool_example_name_plugin with the following methods.

```python
# The default values of the plugin
default_example_name_call: dict,

# Change the values before the tests are run
def augment_rest_call(call: Dict[Str, Str], data: Dict[Str, Any], path: Path) -> None:
  # Do your stuff here
  # call is a merged object from default_example_name_call and the object from the calls.yaml file
  # data is the data from the data.yaml file modified in test steps
  pass

# Make the call
make_example_name_call: FunctionType
```

In case of an error, there should be thrown an ```AssertionError```

The test type is then ```EXAMPLE_NAME```

## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
