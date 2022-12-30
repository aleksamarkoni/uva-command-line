import typer
from rich import print

import uva

app = typer.Typer()


# @app.command()
# def login(username: str = typer.Option(..., prompt=True),
#           password: str = typer.Option(..., prompt=True, confirmation_prompt=True, hide_input=True)):
#     uva = Uva()
#     uva.login(username, password)


@app.command()
def login(username: str = 'aleksamarkoni', password: str = 'nikokaoona'):
    uva.login(username, password)


@app.command()
def logout():
    uva.logout()


@app.command()
def latest_subs(count: int = 10):
    subs = uva.get_latest_subs(count)
    print(subs)


# 1 for ANSI, 2 for JAVA, 3 for C++, 4 for Pascal, 5 for C++11, 6 for Python.
@app.command()
def submit(problem_id: int, filepath: str, language: int):
    uva.submit(problem_id, filepath, language)


if __name__ == "__main__":
    app()
