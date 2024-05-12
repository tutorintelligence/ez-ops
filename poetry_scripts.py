import subprocess


def isort(check: bool = False) -> None:
    check_cmd = ["--check"] if check else []
    subprocess.run(["isort", "."] + check_cmd, check=True)


def black(check: bool = False) -> None:
    check_cmd = ["--check"] if check else []
    subprocess.run(["black", "."] + check_cmd, check=True)


def flake8() -> None:
    subprocess.run(["flake8"], check=True)


def mypy() -> None:
    subprocess.run(["mypy", "."], check=True)


def style() -> None:
    isort()
    black()
    flake8()
    mypy()


def style_check() -> None:
    isort(check=True)
    black(check=True)
    flake8()
    mypy()


def remove_unused() -> None:
    print(
        "Warning - this is a somewhat dangerous operation."
        " It can remove imports with side-effects."
        " Know what you've changed"
    )
    subprocess.run(
        ["autoflake", "--in-place", "--remove-all-unused-imports", "-r", "."],
        check=True,
    )
