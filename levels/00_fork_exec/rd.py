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


def contain(command):
    # TODO: 执行 exec command，注意不同 exec 变体之间的区别
    #       https://docs.python.org/2/library/os.html#os.execv
    # 注意：command 是一个数组（第一个元素是 path/file，整个数组
    #       都会作为 exec 的 args）

    os._exit(0)  # TODO: 添加 exec 后删除这一行


@cli.command(context_settings=dict(ignore_unknown_options=True,))
@click.argument('Command', required=True, nargs=-1)
def run(command):
    # TODO: 用 fork() 替换这里
    #       (https://docs.python.org/2/library/os.html#os.fork)
    pid = 0
    if pid == 0:
        # 这里是 child，我们会尝试在这里做一些 containment
        try:
            contain(command)
        except Exception:
            traceback.print_exc()
            os._exit(1)  # contain() 中出了问题

    # 这里是 parent，pid 包含 fork 出来的 process 的 PID
    # 等待 fork 出来的 child，并获取 exit status
    _, status = os.waitpid(pid, 0)
    print('{} exited with status {}'.format(pid, status))


if __name__ == '__main__':
    cli()
