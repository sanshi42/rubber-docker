# Level 02：mount namespace

我们使用 [unshare()](https://rawgit.com/Fewbytes/rubber-docker/master/docs/linux/index.html#linux.unshare) 调用添加一个 mount namespace。
Mount namespaces 本质上有点像 bind mounts：mount namespace 中的操作会传播到其他 namespaces，*除非* 我们把 parent mount（这里是 /）设为 *private* mount（或类似模式）。
因此，我们需要把 / 改成 private mount。
这通过 [mount()](https://rawgit.com/Fewbytes/rubber-docker/master/docs/linux/index.html#linux.mount) syscall 搭配 `MS_PRIVATE` 和 `MS_REC` flags 完成（为什么需要 `MS_REC`？）

Python 没有暴露 mount syscall；请改用本仓库提供的 `linux` 模块。

**冷知识**：Linux kernel 文档说 private mounts 是默认值，但真的是这样吗？

另外，现在该使用 [mknod()](https://docs.python.org/2/library/os.html#os.mknod) 在 container root 中创建设备节点了：

```python
os.mknod(os.path.join(dev_path, device), 0666 | stat.S_IFCHR, os.makedev(major, minor))
```

查看 host 的 `/dev`，思考你可能需要哪些 devices，记录它们的 minor/major（使用 ls -l），并在 container 中创建它们。

## 相关文档

- [man 2 mount](http://man7.org/linux/man-pages/man2/mount.2.html)
- [Kernel docs - shared mounts](https://www.kernel.org/doc/Documentation/filesystems/sharedsubtree.txt)
- [man 7 namespaces](http://man7.org/linux/man-pages/man7/namespaces.7.html)

## 如何检查你的成果：

### Mount namespace
确认新 fork 出来的 process 位于不同的 mount namespace：
```bash
$ ls -lh /proc/self/ns/mnt
lrwxrwxrwx 1 root root 0 Mar 18 04:13 /proc/self/ns/mnt -> mnt:[4026531840]
$ sudo python rd.py run -i ubuntu /bin/bash
root@ip-172-31-31-83:/# ls -lh /proc/self/ns/mnt
lrwxrwxrwx 1 root root 0 Mar 18 04:13 /proc/self/ns/mnt -> mnt:[4026532139]
```

在 container 内部创建一个新的 mount，并确认外部不可见：
```bash
$ sudo python rd.py run -i ubuntu /bin/bash
root@ip-172-31-31-83:/# mkdir /mnt/moo
root@ip-172-31-31-83:/# mount -t tmpfs tmpfs /mnt/moo

# 保持这个被隔离的 process 运行，并打开另一个 terminal
$ grep moo /proc/mounts
$
```

### 设备节点
我们都喜欢把东西扔到 /dev/null；如果它只是一个普通文件会怎样？
```bash
# 没有 null 设备节点
$ sudo python rd.py run -i ubuntu /bin/bash
root@ip-172-31-31-83:/# find / > /dev/null
root@ip-172-31-31-83:/# ls -lh /dev/null
-rw-r--r-- 1 root root 2.2M Jun 21 16:40 /dev/null

# 有 null 设备节点
$ sudo python rd.py run -i ubuntu /bin/bash
为 container 创建了新的 root fs：/workshop/containers/6aeb472a-94da-42f3-a004-f5809367327b/rootfs
root@ip-172-31-31-83:/# find / > /dev/null
root@ip-172-31-31-83:/# ls -lh /dev/null
crw-r--r-- 1 root root 1, 3 Jun 21 16:44 /dev/null
```

## 清理
别忘了使用 [cleanup.sh](../cleanup.sh) 删除 containers 和 mounts。
