# Level 03: pivot_root

成功使用 [chroot()](https://docs.python.org/2/library/os.html#os.chroot) 把 process 关进 jail 之后，我们来从这个 jail 里逃出去：把 [breakout.py](breakout.py) 脚本复制到 chroot 里并运行它！

```bash
sudo python rd.py run -i ubuntu /bin/bash

# 确认你位于 chroot 内部
ls /

# 逃逸！
python breakout.py

# 然后我们出来了 :)
ls /
```


好吧，显然 [chroot()](https://docs.python.org/2/library/os.html#os.chroot) 还不够。我们试试 [pivot_root()](https://rawgit.com/Fewbytes/rubber-docker/master/docs/linux/index.html#linux.pivot_root)。
记住，[pivot_root()](https://rawgit.com/Fewbytes/rubber-docker/master/docs/linux/index.html#linux.pivot_root) 会作用于 **所有** processes；幸运的是，我们正在使用 mount namespaces。

因为我们使用的 mount namespace 内部使用 mount bind 机制，所以默认情况下，我们的（子）mounts 会被 parent mount（以及 mount namespace）看到。
为了避免这一点，进入新的 mount namespace 后需要立刻把 root mount 设为 private；此外，这一步需要对所有 submounts *递归* 执行，否则最后可能会 unmount 掉 `/dev/pts` 之类的重要内容 :)

使用 [pivot_root()](https://rawgit.com/Fewbytes/rubber-docker/master/docs/linux/index.html#linux.pivot_root) 之后，需要对 `old_root` 执行 [umount2()](https://rawgit.com/Fewbytes/rubber-docker/master/docs/linux/index.html#linux.umount2)。
这里需要使用 umount2 而不是 umount，因为我们需要向调用传入特定 flags；具体来说，需要执行 detach。详情见 `man 2 umount`。

## 相关文档

- [man 2 pivot_root](http://man7.org/linux/man-pages/man2/pivot_root.2.html)
- [man 2 umount2](http://man7.org/linux/man-pages/man2/umount2.2.html)

## 如何检查你的成果

在 container 内部，你应该能看到一个新的 *rootfs* device；不过，这一步实际上会失败：

```
$ sudo python rd.py run -i ubuntu /bin/bash
为 container 创建了新的 root fs：/workshop/containers/f793960b-64bd-4c21-9a7f-da1b0fbe9aad/rootfs
Traceback (most recent call last):
  File "rd.py", line 126, in <module>
    cli()
  File "/usr/local/lib/python2.7/dist-packages/click/core.py", line 700, in __call__
    return self.main(*args, **kwargs)
  File "/usr/local/lib/python2.7/dist-packages/click/core.py", line 680, in main
    rv = self.invoke(ctx)
  File "/usr/local/lib/python2.7/dist-packages/click/core.py", line 1027, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/usr/local/lib/python2.7/dist-packages/click/core.py", line 873, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/usr/local/lib/python2.7/dist-packages/click/core.py", line 508, in invoke
    return callback(*args, **kwargs)
  File "rd.py", line 118, in run
    contain(command, image_name, image_dir, container_id, container_dir)
  File "rd.py", line 98, in contain
    linux.pivot_root(new_root, old_root)
RuntimeError: (16, 'Device or resource busy')
10766 exited with status 256
```

这一步会失败，是因为 [pivot_root(new_root, put_old)](https://rawgit.com/Fewbytes/rubber-docker/master/docs/linux/index.html#linux.pivot_root) 要求 *new_root* 和旧 root 位于不同的 filesystem。
在 step 04 中，我们把 overlay filesystem mount 为 *new_root* 后会解决这个问题。

为了绕过这个问题，可以把 image 文件复制到一个 [tmpfs](https://en.wikipedia.org/wiki/Tmpfs) mount 中。
```python
# ...
# TODO: 取消注释（为什么？）
linux.mount('tmpfs', container_root, 'tmpfs', 0, None)
# ...
```

重复 `breakout.py` 练习，看看你是否还能逃逸 :)
