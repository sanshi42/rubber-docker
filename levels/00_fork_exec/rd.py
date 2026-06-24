#!/usr/bin/env python3
"""从零实现 Docker 工作坊 - Level 0：启动一个新 process。

目标：使用 fork 与 exec 模型启动一个新的 Linux process。

注意：在这个 level 中，我们暂时不关心 containment。

用法：
    运行：
        rd.py run /bin/sh
    会：
        - fork 一个新的 process，并让它 exec '/bin/sh'
        - 同时 parent 等待它结束
"""

import click
import os
import traceback


@click.group()
def cli():
    pass


def contain(command: list[str]):
    os.execvp(command[0], command)


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.argument("Command", required=True, nargs=-1)
def run(command: list[str]):
    if not command:
        raise click.UsageError("You must specify a command")

    pid = os.fork()
    if pid == 0:
        # 这里是 child，我们会尝试在这里做一些 containment
        try:
            contain(command)
        except BaseException:  # noqa
            traceback.print_exc()
            os._exit(127)

    # 这里是 parent，pid 包含 fork 出来的 process 的 PID
    # 等待 fork 出来的 child，并获取 exit status
    _, status = os.waitpid(pid, 0)
    print("{} exited with status {}".format(pid, status))


if __name__ == "__main__":
    cli()
