#!/usr/bin/env python3
"""从零实现 Docker 工作坊 - Level 3：从 chroot 切换到 pivot_root。

目标：使用 pivot_root 代替 chroot，并 umount old_root。

用法：
    运行：
        rd.py run -i ubuntu /bin/sh
    会：
        - 在新的 mount namespace 中 fork 一个带有新 root 的新 process
        - 确保你无法轻易逃逸
"""



import linux
import tarfile
import uuid

import click
import os
import stat
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

    # TODO: 取消注释（为什么？）
    # linux.mount('tmpfs', container_root, 'tmpfs', 0, None)

    with tarfile.open(image_path) as t:
        # 冷知识：tar files 里可能包含 *nix devices！*facepalm*
        members = [m for m in t.getmembers()
                   if m.type not in (tarfile.CHRTYPE, tarfile.BLKTYPE)]
        t.extractall(container_root, members=members)

    return container_root


@click.group()
def cli():
    pass


def makedev(dev_path):
    for i, dev in enumerate(['stdin', 'stdout', 'stderr']):
        os.symlink('/proc/self/fd/%d' % i, os.path.join(dev_path, dev))
    os.symlink('/proc/self/fd', os.path.join(dev_path, 'fd'))
    # 添加额外 devices
    DEVICES = {'null': (stat.S_IFCHR, 1, 3), 'zero': (stat.S_IFCHR, 1, 5),
               'random': (stat.S_IFCHR, 1, 8), 'urandom': (stat.S_IFCHR, 1, 9),
               'console': (stat.S_IFCHR, 136, 1), 'tty': (stat.S_IFCHR, 5, 0),
               'full': (stat.S_IFCHR, 1, 7)}
    for device, (dev_type, major, minor) in DEVICES.items():
        os.mknod(os.path.join(dev_path, device),
                 0o666 | dev_type, os.makedev(major, minor))


def contain(command, image_name, image_dir, container_id, container_dir):
    try:
        linux.unshare(linux.CLONE_NEWNS)  # 创建新的 mount namespace
    except RuntimeError as e:
        if getattr(e, 'args', '') == (1, 'Operation not permitted'):
            print('错误：使用 unshare(2) 搭配 CLONE_NEWNS 需要 '
                  'CAP_SYS_ADMIN capability（也就是说，你可能需要用 sudo '
                  '重试）')
        raise e

    # TODO: 我们在这里加了 MS_REC。猜猜为什么？
    linux.mount(None, '/', None, linux.MS_PRIVATE | linux.MS_REC, None)

    new_root = create_container_root(
        image_name, image_dir, container_id, container_dir)
    print('为 container 创建了新的 root fs：{}'.format(new_root))

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

    makedev(os.path.join(new_root, 'dev'))

    os.chroot(new_root)  # TODO: 替换为 pivot_root

    os.chdir('/')

    # TODO: 对 old root 执行 umount2（提示：查看 man 2 umount 中的 MNT_DETACH）

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
