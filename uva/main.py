import typer
from rich import print

import uva.commands as commands

app = typer.Typer()


@app.command()
def login(
    username: str = typer.Option(
        ...,
        "--username",
        "-u",
        prompt="Enter your uva username",
        show_default=False,
        help="Your uva username"
    ),
    password: str = typer.Option(
        ...,
        "--password",
        "-p",
        prompt="Enter your uva password",
        show_default=False,
        hide_input=True,
        help="Your uva password"
    )
):
    """
        Logs you into the uva portal
    """
    commands.login(username, password)


@app.command()
def logout():
    commands.logout()

@app.command()
def rich():
    from time import sleep

    from rich.console import Console

    console = Console()
    with console.status("[magenta]Covid detector booting up") as status:
        sleep(3)
        console.log("Importing advanced AI")
        sleep(3)
        console.log("Advanced Covid AI Ready")
        sleep(3)
        status.update(status="[bold blue] Scanning for Covid", spinner="earth")
        sleep(3)
        console.log("Found 10,000,000,000 copies of Covid32.exe")
        sleep(3)
        status.update(
            status="[bold red]Moving Covid32.exe to Trash",
            spinner="bouncingBall",
            spinner_style="yellow",
        )
        sleep(5)
    console.print("[bold green]Covid deleted successfully")


@app.command()
def latest_subs(count: int = 10):
    subs = commands.get_latest_subs(count)
    print(subs)


# 1 for ANSI, 2 for JAVA, 3 for C++, 4 for Pascal, 5 for C++11, 6 for Python.
@app.command()
def submit(problem_id: int, filepath: str, language: int):
    commands.submit(problem_id, filepath, language)


if __name__ == "__main__":
    app()
