"""
This is the main file of the plugin. It is called by the test tool and
contains the main function.
"""
from enum import Enum
from json import JSONDecodeError, dumps
from logging import error, info
from pathlib import Path
from typing import IO, Any, Dict, List, Optional, Tuple, TypedDict
from xml.dom.minidom import parseString

from requests import delete, get, post, put


class Assertion(TypedDict):
    """
    This class represents an assertion.
    """

    value: str | Dict[str, Any] | List[Any]
    only_defined: bool


class Cert(TypedDict):
    """
    This class represents a certificate.
    """

    path: Path
    key: Optional[str]


class Method(Enum):
    """
    This class represents the method of the request.
    """

    POST = 1
    GET = 2
    PUT = 3
    DELETE = 4


class Type(Enum):
    """
    This class represents the type of the response.
    """

    XML = 1
    JSON = 2
    TEXT = 3


class File(TypedDict):
    """
    This class represents a file.
    """

    path: str
    binary: bool
    media: str


LoadedFile = Tuple[str, IO[Any], str]
EmptyFile = Tuple[None, str, str]


class RestCall(TypedDict):
    """
    This class represents a rest call.
    """

    # URL
    base_url: str
    path: str
    url: str
    # Request
    method: Method
    data: Optional[str | Dict[str, Any]]
    files: Optional[Dict[str, File | LoadedFile | EmptyFile]]
    multipart: Optional[Dict[str, Tuple[None, str, str]]]
    # payload: Optional[Dict[str, str]]
    # To request
    timeout: int
    headers: Dict
    verify: bool
    cert: Optional[Cert]
    # Verification
    response_type: Type
    assertion: Optional[Assertion]
    hide_logs: bool
    status_codes: List[int]


default_rest_call: RestCall = {
    "base_url": "${REST_BASE_URL}",
    "path": "${REST_PATH}",
    "url": None,  # type: ignore
    "method": "GET",  # type: ignore
    "data": None,
    "files": None,
    "multipart": None,
    # "payload": None,
    # Special
    "timeout": 0,
    "headers": {},
    "verify": False,
    "cert": None,
    # Verification
    "response_type": "JSON",  # type: ignore
    "assertion": None,
    "hide_logs": False,
    "status_codes": [200],
    # url: str | bytes,
    # params: _Params | None = None,
    # *,
    # data: _Data | None = ...,
    # headers: _HeadersMapping | None = ...,
    # cookies: RequestsCookieJar | _TextMapping | None = ...,
    # files: _Files | None = ...,
    # auth: _Auth | None = ...,
    # timeout: _Timeout | None = ...,
    # allow_redirects: bool = ...,
    # proxies: _TextMapping | None = ...,
    # hooks: _HooksInput | None = ...,
    # stream: bool | None = ...,
    # verify: _Verify | None = ...,
    # cert: _Cert | None = ...,
    # json: Any | None = ...
}


def pretty_xml(xml: str) -> str:
    """
    Return a pretty printed xml string.

    Parameters
    ----------
    xml : str
        The xml string.

    Returns
    -------
    str
        The pretty printed xml string.
    """
    dom = parseString(xml)
    return dom.toprettyxml()


def pretty_json(json: str) -> str:
    """
    Return a pretty printed json string.

    Parameters
    ----------
    json : str
        The json string.

    Returns
    -------
    str
        The pretty printed json string.
    """
    return dumps(json, indent=2)


# def multipartify(
#     data, parent_key=None, formatter: Optional[Callable] = None
# ) -> dict:
#     if formatter is None:

#         def formatter(v):
#             return (None, v)  # Multipart representation of value

#     if type(data) is not dict:
#         return {parent_key: formatter(data)}

#     converted = []

#     for key, value in data.items():
#         current_key = key if parent_key is None else f"{parent_key}[{key}]"
#         if type(value) is dict:
#             converted.extend(
#                 multipartify(value, current_key, formatter).items()
#             )
#         elif type(value) is list:
#             for ind, list_value in enumerate(value):
#                 iter_key = f"{current_key}[{ind}]"
#                 converted.extend(
#                     multipartify(list_value, iter_key, formatter).items()
#                 )
#         else:
#             converted.append((current_key, formatter(value)))

#     return dict(converted)


def assert_response(call: RestCall) -> None:
    """
    Assert the response of a rest call.

    Parameters
    ----------
    call : RestCall
        The rest call.

    Raises
    ------
    AssertionError
        If the response is not as expected.
    """
    url = call["url"]

    data: Dict = {"headers": call["headers"]}

    # # Add payload as files
    # if call["payload"]:
    #     if call["files"] == None:
    #         call["files"] = {}
    #     for key, value in call["payload"].items():
    #         call["files"][key] = value

    # Add multipart as files
    if call["multipart"]:
        if call["files"] is None:
            call["files"] = {}
        if call["files"] is not None:
            for key, value in call["multipart"].items():
                call["files"][key] = value

    # Add data or files
    if call["files"]:
        data["files"] = call["files"]
        del data["headers"]["Content-Type"]
    elif call["data"] is not None:
        data["data"] = dumps(call["data"])

    # Add timeout
    if call["timeout"]:
        data["timeout"] = call["timeout"]

    # Add verify
    data["verify"] = call["verify"]

    # url: str | bytes,
    # params: _Params | None = None,
    # *,
    # data: _Data | None = ...,
    # headers: _HeadersMapping | None = ...,
    # cookies: RequestsCookieJar | _TextMapping | None = ...,
    # files: _Files | None = ...,
    # auth: _Auth | None = ...,
    # allow_redirects: bool = ...,
    # proxies: _TextMapping | None = ...,
    # hooks: _HooksInput | None = ...,
    # stream: bool | None = ...,
    # cert: _Cert | None = ...,
    # json: Any | None = ...

    # Make the call
    info(f'Make {call["method"].name} to {url}')
    if call["method"] == Method.GET:
        response = get(url, timeout=10, **data)
    elif call["method"] == Method.POST:
        response = post(url, timeout=10, **data)
    elif call["method"] == Method.PUT:
        response = put(url, timeout=10, **data)
    elif call["method"] == Method.DELETE:
        response = delete(url, timeout=10, **data)

    info(f"Response Status: {response.status_code}")
    if call["hide_logs"] is False:
        try:
            info(f"Response:\n{dumps(response.json(), indent=2)}")
        except JSONDecodeError:
            info(f'Response: "{response.text}"')

    assert response.status_code in call["status_codes"]

    # Compare the response
    if call["assertion"] is not None:
        if isinstance(call["assertion"]["value"], str):
            assert response.text == call["assertion"]["value"]
        elif isinstance(call["assertion"]["value"], dict):
            if call["assertion"]["only_defined"]:
                response_json = response.json()
                assert isinstance(response_json, dict)
                for key, value in call["assertion"]["value"].items():
                    try:
                        msg = (
                            f'Key "{key}": "{value}" not equal to '
                            + f'"{response_json[key]}".'
                        )
                        assert response_json[key] == value, msg
                    except KeyError:
                        assert False, f'Key "{key}" not found in response.'
            else:
                assert response.json() == call["assertion"]
        elif isinstance(call["assertion"]["value"], list):
            assert response.json() == call["assertion"]
        else:
            error(
                f'Assertion type "{type(call["assertion"])}"'
                + " not supported yet."
            )
            assert False


def make_rest_call(
    call: RestCall, data: Dict[str, Any]  # pylint: disable=unused-argument
) -> None:
    """
    Make a rest call.

    Parameters
    ----------
    call : RestCall
        The rest call.
    data : Dict[str, Any]
        The data from the test tool.

    Raises
    ------
    AssertionError
        If the response is not as expected.
    """
    try:
        assert_response(call)
    except AssertionError as e:
        # Log the expected response
        if call["assertion"] is not None:
            if call["response_type"] == Type.XML:
                error(f'Expexted:\n{pretty_xml(str(call["assertion"]))}')
            elif call["response_type"] == Type.JSON:
                error(f'Expexted:\n{pretty_json(str(call["assertion"]))}')
            else:
                error(f'Expexted:\n{call["assertion"]}')
            raise e


def augment_rest_call(
    call: RestCall, data: Dict, path: Path  # pylint: disable=unused-argument
) -> None:
    """
    Augment a rest call.

    Parameters
    ----------
    call : RestCall
        The rest call.
    data : Dict
        The data from the test tool.
    path : Path
        The project path.
    """
    # Base URL
    if not isinstance(call["base_url"], str):
        raise ValueError("Base URL must be a string.")

    # Path
    if not isinstance(call["path"], str):
        raise ValueError("Path must be a string.")

    # Augment the url
    if call["url"] is None:
        call["url"] = f'{call["base_url"]}{call["path"]}'
    elif not isinstance(call["url"], str):
        raise ValueError("URL must be a string.")

    # Method
    if not isinstance(call["method"], str):
        raise ValueError("Method must be a string.")
    else:
        try:
            call["method"] = Method[call["method"]]
        except KeyError as e:
            raise ValueError("Method is not supported.") from e

    # Data

    # Files
    if call["files"] is not None:
        for key, file in call["files"].items():
            if isinstance(file, dict):
                if file["binary"]:
                    file_type = "rb"
                else:
                    file_type = "r"
                open_file = open(path.joinpath(file["path"]), file_type)
                call["files"][key] = (
                    file["path"],
                    open_file,
                    file["media"],
                )
            else:
                raise ValueError("File is not a dict.")
    # Multipart
    if call["multipart"] is not None:
        for key, part in call["multipart"].items():
            call["multipart"][key] = (None, dumps(part), "application/json")

    # Payload
    # if call['payload'] is not None:
    #     call["payload"] = multipartify(call["payload"])

    # Timeout
    if not isinstance(call["timeout"], int):
        raise ValueError("Timeout must be an integer, set 0 to disable.")

    # Headers
    if call["headers"] is None:
        raise ValueError("Headers are requiered.")
    elif not isinstance(call["headers"], dict):
        raise ValueError("Headers must be a dict.")

    # Verify
    if not isinstance(call["verify"], bool):
        raise ValueError("Verify must be a boolean.")

    # Cert
    if call["cert"] is not None:
        if call["cert"]["path"] is not None:
            if Path(call["cert"]["path"]).is_absolute():
                call["cert"]["path"] = path.joinpath(call["cert"]["path"])
            else:
                call["cert"]["path"] = path.joinpath(call["cert"]["path"])
        else:
            raise ValueError("Cert path is requiered for cert.")

        if call["cert"]["key"] is not None:
            if not isinstance(call["cert"]["key"], str):
                raise ValueError("Cert key must be a string.")

    # Response type
    if not isinstance(call["response_type"], str):
        raise ValueError("Response type must be a string.")
    else:
        try:
            call["response_type"] = Type[call["response_type"]]
        except KeyError as e:
            raise ValueError("Response type is not supported.") from e

    # Assertion
    if call["assertion"] is not None:
        if not isinstance(call["assertion"], dict):
            raise ValueError("Assertion must be a dict.")

        # Default only_defined
        if ("only_defined" in call["assertion"] and
                call["assertion"]["only_defined"] is not None):
            if not isinstance(call["assertion"]["only_defined"], bool):
                raise ValueError("Only defined must be a boolean.")
        else:
            call["assertion"]["only_defined"] = False

        # Value is requiered
        if ("value" not in call["assertion"] or
                call["assertion"]["value"] is None):
            raise ValueError("Assertion value is requiered.")

        if (not isinstance(call["assertion"]["value"], str)) and (
            not isinstance(call["assertion"]["value"], dict)
        ):
            raise ValueError("Assertion must be a string or a dict.")

    # Hide logs
    if not isinstance(call["hide_logs"], bool):
        raise ValueError("Hide logs must be a boolean.")

    # Status codes
    if not isinstance(call["status_codes"], list):
        raise ValueError("Status codes must be a list.")
    else:
        for status_code in call["status_codes"]:
            if not isinstance(status_code, int):
                raise ValueError("Status codes must be integers.")


def main() -> None:
    """
    The main function of the plugin.
    """
    print("test-tool-rest-plugin")
