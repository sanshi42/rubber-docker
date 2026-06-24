# Level 08: CPU CGroup

在这个 Level 中，我们添加第一个 cgroup：
- 首先，为所有 containers 创建一个顶层 cgroup，并为每个 container 创建一个 subgroup，类似 `/sys/fs/cgroup/cpu/rubber-docker/<container_id>`。
- 然后，把被隔离的 process 的 pid 写入该 group 的 `tasks` 文件，把它移动到这个 group。
- 最后，把分配的 shares 数量写入 `cpu.shares`，设置该 group 的限制。

## 相关文档
- [Kernel docs, scheduler design](https://www.kernel.org/doc/Documentation/scheduler/sched-design-CFS.txt) - section 7
- [Kernel docs, CPU accounting controller](https://www.kernel.org/doc/Documentation/cgroup-v1/cpuacct.txt)


## 练习
- 用 200 cpu shares 运行一个 container，然后在 container 内生成 cpu load（使用 `stress` 工具）。host 显示了多少 cpu usage？为什么？
- 运行两个 shares 分配不同的 containers，在两个 container 内都生成 cpu load，并在 host 上用 top 观察 cpu usage。
- cgroup limits 与 `nice` priorities、priority classes（例如 RT scheduler）之间有什么相互作用？

## 如何检查你的成果
在 container 内查看 `/proc/self/cgroup` 的内容，确认它位于新的 cpu cgroup：
```
$ sudo python rd.py run -i ubuntu /bin/bash
为 container 创建了新的 root fs：/workshop/containers/57f02a16-4515-4068-b097-b241b66e4987/rootfs
root@57f02a16-4515-4068-b097-b241b66e4987:/# cat /proc/self/cgroup
10:hugetlb:/user.slice/user-1000.slice/session-2.scope
9:blkio:/user.slice/user-1000.slice/session-2.scope
8:net_cls,net_prio:/user.slice/user-1000.slice/session-2.scope
7:cpu,cpuacct:/rubber_docker/57f02a16-4515-4068-b097-b241b66e4987
6:perf_event:/user.slice/user-1000.slice/session-2.scope
5:devices:/user.slice/user-1000.slice/session-2.scope
4:cpuset:/user.slice/user-1000.slice/session-2.scope
3:memory:/user.slice/user-1000.slice/session-2.scope
2:freezer:/user.slice/user-1000.slice/session-2.scope
1:name=systemd:/user.slice/user-1000.slice/session-2.scope

root@57f02a16-4515-4068-b097-b241b66e4987:/# grep 57f02a16-4515-4068-b097-b241b66e4987 /proc/self/cgroup
7:cpu,cpuacct:/rubber_docker/57f02a16-4515-4068-b097-b241b66e4987
```

另外，也可以在 host 上查看 `/sys/fs/cgroup/cpu`：
```
$ cat /sys/fs/cgroup/cpu/rubber_docker/57f02a16-4515-4068-b097-b241b66e4987/tasks
5386
```
