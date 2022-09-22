from invoke import task


@task
def app(ctx):
    ctx.run("uvicorn --app-dir ./src/app main:app", pty=True)


@task
def test(ctx):
    ctx.run("pytest --disable-warnings src", pty=True)


@task
def coverage(ctx):
    ctx.run("coverage run --branch -m pytest --disable-warnings src", pty=True)


@task(coverage)
def coverage_report(ctx):
    ctx.run("coverage html", pty=True)
