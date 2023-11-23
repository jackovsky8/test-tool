"""Python setup.py for test_tool package"""
import io
import os
from setuptools import find_packages, setup


def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("test_tool", "VERSION")
    '0.1.0'
    >>> read("README.md")
    ...
    """

    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def read_requirements(path):
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]


setup(
    name="universal-test-tool",
    version=read("test_tool", "VERSION"),
    description="Awesome test-tool to make tests configurable with a yaml file.",
    url="https://github.com/jackovsky8/test-tool/",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="jackovsky8",
    packages=find_packages(exclude=["tests", ".github"]),
    install_requires=read_requirements("requirements.txt"),
    entry_points={
        "console_scripts": [
            "test-tool = test_tool.__main__:main",
            "test-tool-bash-cmd-plugin = test_tool_bash_cmd_plugin.__main__:main",
            "test-tool-copy-files-ssh-plugin = test_tool_copy_files_ssh_plugin.__main__:main",
            "test-tool-jdbc-sql-plugin = test_tool_jdbc_sql_plugin.__main__:main",
            "test-tool-rest-plugin = test_tool_rest_plugin.__main__:main",
            "test-tool-ssh-cmd-plugin = test_tool_ssh_cmd_plugin.__main__:main"
        ]
    },
    extras_require={"test": read_requirements("requirements-test.txt")},
)
