#!/usr/bin/env python3
"""从零实现 Docker 工作坊 - Level 1：chroot 到一个 image 中。

目标：使用经典的 chroot 获得一些 filesystem isolation。

用法：
    运行：
        rd.py run -i ubuntu /bin/sh
    会：
        fork 一个新的 child process，它会：
           - 把一个 ubuntu image 解包到新目录
           - chroot() 到该目录
           - exec '/bin/sh'
        同时 parent 等待它结束。
"""


import os
import tarfile
import uuid

import click
import traceback

import linux


def _get_image_path(image_name, image_dir, image_suffix='tar'):
    return os.path.join(image_dir, os.extsep.join([image_name, image_suffix]))


def _get_container_path(container_id, container_dir, *subdir_names):
    return os.path.join(container_dir, container_id, *subdir_names)


def create_container_root(image_name, image_dir, container_id, container_dir):
    """通过把 image 解压到新目录来创建 container root。

    用法：
    new_root = create_container_root(
        image_name, image_dir, container_id, container_dir)

    @param image_name: 要解压的 image 名称
    @param image_dir: 查找 image tarballs 的目录
    @param container_id: 唯一的 container id
    @param container_dir: 新生成 container 目录的基础目录
    @retrun: 新的 container root 目录
    @rtype: str
    """
    image_path = _get_image_path(image_name, image_dir)
    container_root = _get_container_path(container_id, container_dir, 'rootfs')

    assert os.path.exists(image_path), "无法找到 image %s" % image_name

    if not os.path.exists(container_root):
        os.makedirs(container_root)

    with tarfile.open(image_path) as t:
        # 冷知识：tar files 里可能包含 *nix devices！*facepalm*
        members = [m for m in t.getmembers()
                   if m.type not in (tarfile.CHRTYPE, tarfile.BLKTYPE)]
        t.extractall(container_root, members=members)

    return container_root


@click.group()
def cli():
    pass


def contain(command, image_name, image_dir, container_id, container_dir):
    # TODO: 在 chroot 之前做必要准备
    # print('为 container 创建了新的 root fs：{}'.format(new_root))

    # TODO: 执行 chroot 到 new_root
    # TODO: chroot 之后做必要准备（提示：试着运行：python3 rd.py run -i ubuntu -- /bin/sh）

    os.execvp(command[0], command)


@cli.command(context_settings=dict(ignore_unknown_options=True,))
@click.option('--image-name', '-i', help='image 名称', default='ubuntu')
@click.option('--image-dir', help='images 目录',
              default='/workshop/images')
@click.option('--container-dir', help='containers 目录',
              default='/workshop/containers')
@click.argument('Command', required=True, nargs=-1)
def run(image_name, image_dir, container_dir, command):
    container_id = str(uuid.uuid4())
    pid = os.fork()
    if pid == 0:
        # 这里是 child，我们会尝试在这里做一些 containment
        try:
            contain(command, image_name, image_dir, container_id,
                    container_dir)
        except Exception:
            traceback.print_exc()
            os._exit(1)  # contain() 中出了问题

    # 这里是 parent，pid 包含 fork 出来的 process 的 PID
    # 等待 fork 出来的 child，并获取 exit status
    _, status = os.waitpid(pid, 0)
    print('{} exited with status {}'.format(pid, status))


if __name__ == '__main__':
    cli()
