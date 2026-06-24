# Level 07：network namespace

移动到新的 network namespace，让 container 无法访问 host NICs。
实现之后，可以用 `ip link` 或 `ifconfig` 检查，确认已经看不到 host NICs。

Bonus：iproute2 工具链也允许操作 network namespaces。
看看 `ip netns` 命令。
为了让它能和我们用 syscalls 生成的 namespaces 配合工作，需要把 `/var/run/netns` 中的某个文件链接到来自 `/proc/<pid>/ns/` 的 network namespace file descriptor。

## 相关文档

- [Namespaces in operation - network namespace](https://lwn.net/Articles/580893/)
- [man ip-netns](http://man7.org/linux/man-pages/man8/ip-netns.8.html)

## 如何检查你的成果
运行 container，并使用 `ip link` 或 `ifconfig` 查看可用 NICs。
你应该只看到 `lo`（如果使用 `ip link`），或者看不到任何 NICs（如果使用 `ifconfig`）。
```
$ sudo python rd.py run -i ubuntu /bin/bash
为 container 创建了新的 root fs：/workshop/containers/9feb3d2d-725b-4c36-8c4d-0c586766f6f6/rootfs
root@9feb3d2d-725b-4c36-8c4d-0c586766f6f6:/# ip a
1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN group default
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
root@9feb3d2d-725b-4c36-8c4d-0c586766f6f6:/# ifconfig
```

## Bonus round
`ip netns` 命令允许你操控 network namespaces，例如创建一对 `veth`，并把其中一端分配给新的 network namespace。
`veth` pair 有点像一根 patch cable：发送到一个 `veth` NIC 的 packets 会出现在这对设备的另一端。
你可以使用 `veth` 把 container 连接到 bridge/vswitch（就像 Docker 做的那样）或 routing table。
`ip netns` 使用 `netlink` kernel API，你也可以直接通过 `pyroute2` 模块使用它。
另一种方式是先从运行 `ip netns` 命令开始，这可能更简单。
注意，`ip netns` 要求 network namespace file descriptor 位于 `/var/run/netns`，你可以 symlink `/proc/<pid>/ns/net` 来让 `ip netns` 工作。
