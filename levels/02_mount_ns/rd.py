#!/usr/bin/env python3
"""从零实现 Docker 工作坊 - Level 2：添加 mount namespace。

目标：把我们的 mount table 和其他 processes 分开。

用法：
    运行：
        rd.py run -i ubuntu /bin/sh
    会：
        - 在新的 mount namespace 中 fork 一个新的 chrooted process
"""



import linux
import tarfile
import uuid

import click
import os
import traceback


def _get_image_path(image_name, image_dir, image_suffix='tar'):
    return os.path.join(image_dir, os.extsep.join([image_name, image_suffix]))


def _get_container_path(container_id, container_dir, *subdir_names):
    return os.path.join(container_dir, container_id, *subdir_names)


def create_container_root(image_name, image_dir, container_id, container_dir):
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
    new_root = create_container_root(
        image_name, image_dir, container_id, container_dir)
    print('为 container 创建了新的 root fs：{}'.format(new_root))

    # TODO: 是时候告别旧的 mount namespace 了，
    #       查看 "man 2 unshare" 获取帮助
    #   提示 1：没有 os.unshare()，该使用我们专门为你准备的 linux 模块了！
    #   提示 2：linux 模块同时包含函数和常量！
    #           e.g. linux.CLONE_NEWNS

    # TODO: 还记得 shared subtrees 吗？
    # (https://www.kernel.org/doc/Documentation/filesystems/sharedsubtree.txt)
    # 把 / 设为 private mount，避免污染 host mount table。

    # 在 new_root 下创建 mounts（/proc、/sys、/dev）
    linux.mount('proc', os.path.join(new_root, 'proc'), 'proc', 0, '')
    linux.mount('sysfs', os.path.join(new_root, 'sys'), 'sysfs', 0, '')
    linux.mount('tmpfs', os.path.join(new_root, 'dev'), 'tmpfs',
                linux.MS_NOSUID | linux.MS_STRICTATIME, 'mode=755')
    # 添加一些基础 devices
    devpts_path = os.path.join(new_root, 'dev', 'pts')
    if not os.path.exists(devpts_path):
        os.makedirs(devpts_path)
        linux.mount('devpts', devpts_path, 'devpts', 0, '')
    for i, dev in enumerate(['stdin', 'stdout', 'stderr']):
        os.symlink('/proc/self/fd/%d' % i, os.path.join(new_root, 'dev', dev))

    # TODO: 使用 os.mknod 添加更多 devices（例如 null、zero、random、urandom）。

    os.chroot(new_root)

    os.chdir('/')

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
            contain(command, image_name, image_dir, container_id, container_dir)
        except Exception:
            traceback.print_exc()
            os._exit(1)  # contain() 中出了问题

    # 这里是 parent，pid 包含 fork 出来的 process 的 PID
    # 等待 fork 出来的 child，并获取 exit status
    _, status = os.waitpid(pid, 0)
    print('{} exited with status {}'.format(pid, status))


if __name__ == '__main__':
    cli()
