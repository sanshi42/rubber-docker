# Level 06: PID namespace

PID namespace 和其他 namespaces 略有不同：`unshare()` 不会把当前 process 移动到新的 namespace，而是只有它未来的 children 会进入新的 PID namespace。
我们有 2 个选择：
 1. 在 fork 之前使用 `unshare()`
 1. 使用 `clone()` 代替 `fork()`，并传入 `CLONE_NEWPID` flag

`linux` 模块暴露的 `clone()` 版本模仿了 `libc` API（因为这样更简单）：
```python
linux.clone(python_callable, flags, callable_args_tuple) # --> returns pid of new process
```

## 练习
- 尝试在没有 `/proc` mount，或 bind mount 原始 `/proc` mount 的情况下使用 PID namespace。此时 `ps` 之类的工具表现如何？
- 分别在有 PID namespace 和没有 PID namespace 的 container 内尝试 `kill -9 $$`（$$ 会求值为当前 PID）。两者有区别吗？为什么？
- 尝试在 container 内生成 zombies。

## 相关文档

- [man 7 pid_namespaces](http://man7.org/linux/man-pages/man7/pid_namespaces.7.html)
- [Namespaces in operation part 3](https://lwn.net/Articles/531419/)

## 如何检查你的成果

各种 process listing 命令和 */proc* filesystem 应该只显示 container processes：
```
$ sudo python rd.py run -i ubuntu /bin/bash
为 container 创建了新的 root fs：/workshop/containers/a4725e53-b164-4b60-ab6f-8ee527258f71/rootfs
root@a4725e53-b164-4b60-ab6f-8ee527258f71:/# ps
  PID TTY          TIME CMD
    1 pts/0    00:00:00 bash
   11 pts/0    00:00:00 ps
root@a4725e53-b164-4b60-ab6f-8ee527258f71:/# ls /proc | grep '[0-9]'
1
12
13
```
