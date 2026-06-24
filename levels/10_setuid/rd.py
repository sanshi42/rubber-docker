#!/usr/bin/env python3
"""从零实现 Docker 工作坊 - Level 10：exec 非 root containers。

目标：允许指定 uid 和 gid，让 container 以非 root user 身份运行。
"""




import linux
import tarfile
import uuid

import click
import os
import stat


def _get_image_path(image_name, image_dir, image_suffix='tar'):
    return os.path.join(image_dir, os.extsep.join([image_name, image_suffix]))


def _get_container_path(container_id, base_path, *subdir_names):
    return os.path.join(base_path, container_id, *subdir_names)


def create_container_root(image_name, image_dir, container_id, container_dir):
    image_path = _get_image_path(image_name, image_dir)
    image_root = os.path.join(image_dir, image_name, 'rootfs')

    assert os.path.exists(image_path), "无法找到 image %s" % image_name

    if not os.path.exists(image_root):
        os.makedirs(image_root)
        with tarfile.open(image_path) as t:
            # 冷知识：tar files 里可能包含 *nix devices！*facepalm*
            members = [m for m in t.getmembers()
                       if m.type not in (tarfile.CHRTYPE, tarfile.BLKTYPE)]
            t.extractall(image_root, members=members)

    # 创建 copy-on-write（uppperdir）、overlay workdir
    # 和 mount point 所需的目录
    container_cow_rw = _get_container_path(
        container_id, container_dir, 'cow_rw')
    container_cow_workdir = _get_container_path(
        container_id, container_dir, 'cow_workdir')
    container_rootfs = _get_container_path(
        container_id, container_dir, 'rootfs')
    for d in (container_cow_rw, container_cow_workdir, container_rootfs):
        if not os.path.exists(d):
            os.makedirs(d)

    # mount overlay（提示：使用 MS_NODEV flag 来 mount）
    linux.mount(
        'overlay', container_rootfs, 'overlay', linux.MS_NODEV,
        "lowerdir={image_root},upperdir={cow_rw},workdir={cow_workdir}".format(
            image_root=image_root,
            cow_rw=container_cow_rw,
            cow_workdir=container_cow_workdir))

    return container_rootfs  # 返回 overlayfs 的 mountpoint


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


def _setup_cpu_cgroup(container_id, cpu_shares):
    CPU_CGROUP_BASEDIR = '/sys/fs/cgroup/cpu'
    container_cpu_cgroup_dir = os.path.join(
        CPU_CGROUP_BASEDIR, 'rubber_docker', container_id)

    # 把 container 放进名为 'rubber_docker/container_id' 的新 cpu cgroup
    if not os.path.exists(container_cpu_cgroup_dir):
        os.makedirs(container_cpu_cgroup_dir)
    tasks_file = os.path.join(container_cpu_cgroup_dir, 'tasks')
    open(tasks_file, 'w').write(str(os.getpid()))

    # 如果 (cpu_shares != 0)，就在我们的 cpu cgroup 中设置 'cpu.shares'
    if cpu_shares:
        cpu_shares_file = os.path.join(container_cpu_cgroup_dir, 'cpu.shares')
        open(cpu_shares_file, 'w').write(str(cpu_shares))


def _setup_memory_cgroup(container_id, memory, memory_swap):
    MEMORY_CGROUP_BASEDIR = '/sys/fs/cgroup/memory'
    container_mem_cgroup_dir = os.path.join(
        MEMORY_CGROUP_BASEDIR, 'rubber_docker', container_id)

    # 把 container 放进名为 'rubber_docker/container_id' 的新 memory cgroup
    if not os.path.exists(container_mem_cgroup_dir):
        os.makedirs(container_mem_cgroup_dir)
    tasks_file = os.path.join(container_mem_cgroup_dir, 'tasks')
    open(tasks_file, 'w').write(str(os.getpid()))

    if memory is not None:
        mem_limit_in_bytes_file = os.path.join(
            container_mem_cgroup_dir, 'memory.limit_in_bytes')
        open(mem_limit_in_bytes_file, 'w').write(str(memory))
    if memory_swap is not None:
        memsw_limit_in_bytes_file = os.path.join(
            container_mem_cgroup_dir, 'memory.memsw.limit_in_bytes')
        open(memsw_limit_in_bytes_file, 'w').write(str(memory_swap))


def contain(command, image_name, image_dir, container_id, container_dir,
            cpu_shares, memory, memory_swap, user):
    _setup_cpu_cgroup(container_id, cpu_shares)
    _setup_memory_cgroup(container_id, memory, memory_swap)

    linux.sethostname(container_id)  # 把 hostname 改成 container_id

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

    # TODO: 如果设置了 user，使用 os.setuid() 降低 privileges
    #       （也可以选择使用 os.setgid()）。

    os.execvp(command[0], command)


@cli.command(context_settings=dict(ignore_unknown_options=True,))
@click.option('--memory',
              help='Memory limit，单位为 bytes。'
              ' 可使用后缀表示更大的单位（k、m、g）',
              default=None)
@click.option('--memory-swap',
              help='等于 memory 加 swap 的正整数。'
              ' 指定 -1 可启用无限 swap。',
              default=None)
@click.option('--cpu-shares', help='CPU shares（相对权重）', default=0)
@click.option('--user', help='UID (format: <uid>[:<gid>])', default='')
@click.option('--image-name', '-i', help='image 名称', default='ubuntu')
@click.option('--image-dir', help='images 目录',
              default='/workshop/images')
@click.option('--container-dir', help='containers 目录',
              default='/workshop/containers')
@click.argument('Command', required=True, nargs=-1)
def run(memory, memory_swap, cpu_shares, user, image_name, image_dir,
        container_dir, command):
    container_id = str(uuid.uuid4())

    # linux.clone(callback, flags, callback_args) 是仿照 Glibc
    # 版本建模的。见："man 2 clone"
    flags = (linux.CLONE_NEWPID | linux.CLONE_NEWNS | linux.CLONE_NEWUTS |
             linux.CLONE_NEWNET)
    callback_args = (command, image_name, image_dir, container_id,
                     container_dir, cpu_shares, memory, memory_swap, user)
    pid = linux.clone(contain, flags, callback_args)

    # 这里是 parent，pid 包含 fork 出来的 process 的 PID
    # 等待 fork 出来的 child，并获取 exit status
    _, status = os.waitpid(pid, 0)
    print('{} exited with status {}'.format(pid, status))


if __name__ == '__main__':
    cli()
