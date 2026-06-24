# Level 10: setuid

在这个 level 中，我们实现类似 `docker run -u UID` 的功能：以非 root user 运行 processes。
为了让被隔离的 process 以不同 user 运行，请使用 _setuid_ 和 _setgid_ system calls。
这些 system calls 必须在 _exec_ 之前调用，但要在所有需要 root privileges 的任务完成之后调用。

## 练习
- 使用已有 username 的 uid（例如 1000），并试着修改 container 的 _/etc/passwd_ 文件。
- 在 container 内创建一些文件，然后在 container 外观察 owner uid。这会如何影响 containers 之间的 shared volumes？

## 相关文档

- [man 2 setuid](hhttp://man7.org/linux/man-pages/man2/setuid.2.html)

## 如何检查你的成果
```
$ sudo python rd.py run -i ubuntu --user 2014:222 /bin/bash
为 container 创建了新的 root fs：/workshop/containers/1e9b16b3-3ea3-4cad-84e1-f623ba4deada/rootfs
root@1e9b16b3-3ea3-4cad-84e1-f623ba4deada:/# id

```
