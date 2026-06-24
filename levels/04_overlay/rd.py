#!/usr/bin/env python3
"""从零实现 Docker 工作坊 - Level 4：添加 overlay FS。

目标：不再重复解压 image，而是把它用作 read-only layer（lowerdir），
      并为变更创建 copy-on-write layer（upperdir）。

提示：别忘了 overlay fs 还需要一个 workdir。

在这里阅读更多 overlay FS 信息：
https://www.kernel.org/doc/Documentation/filesystems/overlayfs.txt
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
    assert os.path.exists(image_path), "无法找到 image %s" % image_name

    # TODO: 不要创建 container_root 并解压到里面，
    #       而是创建 images_root。
    # 每个 image 只保留一个 rootfs，并复用它
    container_root = _get_container_path(container_id, container_dir, 'rootfs')

    if not os.path.exists(container_root):
        os.makedirs(container_root)
        with tarfile.open(image_path) as t:
            # 冷知识：tar files 里可能包含 *nix devices！*facepalm*
            members = [m for m in t.getmembers()
                       if m.type not in (tarfile.CHRTYPE, tarfile.BLKTYPE)]
            t.extractall(container_root, members=members)

    # TODO: 创建 copy-on-write（uppperdir）、overlay workdir
    #       和 mount point 所需的目录

    # TODO: 执行 overlay mount（提示：使用 MS_NODEV flag 来 mount）

    return container_root  # 返回已 mount overlayfs 的 mountpoint


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


def _create_mounts(new_root):
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


def contain(command, image_name, image_dir, container_id, container_dir):
    linux.unshare(linux.CLONE_NEWNS)  # 创建新的 mount namespace

    linux.mount(None, '/', None, linux.MS_PRIVATE | linux.MS_REC, None)

    new_root = create_container_root(
        image_name, image_dir, container_id, container_dir)
    print('为 container 创建了新的 root fs：{}'.format(new_root))

    _create_mounts(new_root)

    old_root = os.path.join(new_root, 'old_root')
    os.makedirs(old_root)
    linux.pivot_root(new_root, old_root)

    os.chdir('/')

    linux.umount2('/old_root', linux.MNT_DETACH)  # umount old root
    os.rmdir('/old_root')  # rmdir old_root 目录
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
