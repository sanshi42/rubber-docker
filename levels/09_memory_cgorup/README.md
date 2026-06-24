# Level 09: Memory CGroup

在这个 level 中，我们限制 container 的 memory usage。
和 cpu cgroup 中一样，为每个 container 在 memory cgroup fs 里创建一个目录。
把 pid 写入 `tasks` 文件，将 process 移动到这个 cgroup，然后通过写入以下文件来设置 limits：
- `memory.limit_in_bytes` - 字节数或单位值，例如 1g
- `memory.memsw.limit_in_bytes` - 字节数或单位值，例如 1g

## 练习

设置 limits 后，使用 stress 工具运行一个 container，观察 container 超过分配 limit 时会发生什么。
探索 container 的行为：
- 观察 container 超过 `memory.limit_in_bytes` 时的情况。
- 观察 container 超过 `memory.memsw.limit_in_bytes.` 时的情况。
- 观察 `memory.kmem.usage_in_bytes`，所有已使用的 kernel memory 都被统计了吗？
- 在 container 内尝试臭名昭著的 `while true; do mkdir t; cd t; done` DOS 攻击。它能成功 DOS host 吗？
- `tcp` socket buffers memory 记在哪里？`udp` memory 记在哪里？
- 用不同 OOM control options 探索 memory cgroup 的行为（`memory.oom_control` 文件）。

## 相关文档
- [Kernel docs, memory cgroup](https://www.kernel.org/doc/Documentation/cgroup-v1/memory.txt)


## 如何检查你的成果
从 container 内部查看：
```
$ sudo python rd.py run -i ubuntu --memory 128m --memory-swap 150m /bin/bash
为 container 创建了新的 root fs：/workshop/containers/1e9b16b3-3ea3-4cad-84e1-f623ba4deada/rootfs
root@1e9b16b3-3ea3-4cad-84e1-f623ba4deada:/# cat /proc/self/cgroup
10:hugetlb:/user.slice/user-1000.slice/session-2.scope
9:blkio:/user.slice/user-1000.slice/session-2.scope
8:net_cls,net_prio:/user.slice/user-1000.slice/session-2.scope
7:cpu,cpuacct:/rubber_docker/1e9b16b3-3ea3-4cad-84e1-f623ba4deada
6:perf_event:/user.slice/user-1000.slice/session-2.scope
5:devices:/user.slice/user-1000.slice/session-2.scope
4:cpuset:/user.slice/user-1000.slice/session-2.scope
3:memory:/rubber_docker/1e9b16b3-3ea3-4cad-84e1-f623ba4deada
2:freezer:/user.slice/user-1000.slice/session-2.scope
1:name=systemd:/user.slice/user-1000.slice/session-2.scope
```

从 host 查看：
```
$ cat /sys/fs/cgroup/memory/rubber_docker/1e9b16b3-3ea3-4cad-84e1-f623ba4deada/memory.limit_in_bytes
134217728
$ cat /sys/fs/cgroup/memory/rubber_docker/1e9b16b3-3ea3-4cad-84e1-f623ba4deada/memory.memsw.limit_in_bytes
157286400
```

## Bonus round
阅读并使用以下 control files：
- `memory.oom_control`
- `memory.swappiness`
- `memory.kmem.limit_in_bytes`
- `memory.kmem.tcp.limit_in_bytes`
- `memory.soft_limit_in_bytes`
