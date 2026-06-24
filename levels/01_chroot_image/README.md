# Level 01: chroot

把一个 process “关进 jail”，让它看不到文件系统的其他部分。

要在 chroot 中 exec 一个 process，我们需要几样东西：
 1. 为 process 选择一个新的 root directory
   1. 里面包含我们的 target binary
   1. 里面包含其他依赖（proc？sys？dev？）
 1. 使用 Python 的 [os.chroot](https://docs.python.org/2/library/os.html#os.chroot) chroot 到其中

为了帮你快速开始，我们实现了 *create_container_root()*，它会解压预先下载好的 images（ubuntu 或 busybox），并返回一个路径。

如果希望 `ps` 之类的工具正常工作，需要在新的 root 里 mount `/proc`、`/sys` 和 `/dev` 这些特殊 filesystems。
这可以通过 [linux Python 模块](https://rawgit.com/Fewbytes/rubber-docker/master/docs/linux/index.html)完成；它暴露了 [mount()](https://rawgit.com/Fewbytes/rubber-docker/master/docs/linux/index.html#linux.mount) syscall：

```python
linux.mount('proc', os.path.join(new_root, 'proc'), 'proc', 0, '')
```
*mount()* syscall 的语义被完整保留下来；想了解更多请阅读 `man 2 mount`。

在 chroot 内部查看 `/proc/mounts`。它和 chroot 外部的 `/proc/mounts` 看起来有什么不同吗？
记住，我们还没有使用 mount namespace！

(*答案*: [Github 上的 linux/fs/proc_namespace.c](https://github.com/torvalds/linux/blob/33caf82acf4dc420bf0f0136b886f7b27ecf90c5/fs/proc_namespace.c#L110))

## 清理

完成这个 level 后，你可能会注意到 */proc/mounts* 里有很多未使用的条目，*/workshop/containers* 里也有很多未使用的已解压 images。可以使用[我们的清理脚本](../cleanup.sh)快速删除它们。
```bash
/workshop/rubber-docker/levels/cleanup.sh
```

## 相关文档

[chroot manpage](http://man7.org/linux/man-pages/man2/chroot.2.html)

## 如何检查你的成果

不调用 `chroot`（_错误_）：
```shell
$ python3 rd.py run -i ubuntu -- /bin/ls -l /workshop/rubber-docker/levels/
total 44
drwxr-xr-x 2 ubuntu ubuntu 4096 Jun 20 21:37 00_fork_exec
drwxr-xr-x 2 ubuntu ubuntu 4096 Jun 20 21:37 01_chroot_image
drwxr-xr-x 2 ubuntu ubuntu 4096 Jun 20 21:37 02_mount_ns
drwxr-xr-x 2 ubuntu ubuntu 4096 Jun 20 21:37 03_pivot_root
drwxr-xr-x 2 ubuntu ubuntu 4096 Jun 20 21:37 04_overlay
drwxr-xr-x 2 ubuntu ubuntu 4096 Jun 20 21:37 05_uts_namespace
drwxr-xr-x 2 ubuntu ubuntu 4096 Jun 20 21:37 06_pid_namespace
drwxr-xr-x 2 ubuntu ubuntu 4096 Jun 20 21:37 07_net_namespace
drwxr-xr-x 2 ubuntu ubuntu 4096 Jun 20 21:37 08_cpu_cgroup
drwxr-xr-x 2 ubuntu ubuntu 4096 Jun 20 21:37 09_memory_cgorup
drwxr-xr-x 2 ubuntu ubuntu 4096 Jun 20 21:37 10_setuid
1620 exited with status 0
```

使用 `chroot` 和已解压 image（_正确_）：
```shell
$ python3 rd.py run -i ubuntu -- /bin/ls -l /workshop/rubber-docker/levels/
为 container 创建了新的 root fs：/workshop/containers/1739af4b-3849-4e88-ae65-dc98264a0e69/rootfs
/bin/ls: cannot access /workshop/rubber-docker/levels/: No such file or directory
1656 exited with status 512
```
