# Linux containers 基础

# 什么是 Linux container？

container，有时也被称为“O/S virtualization”，指的是操作系统中一组被隔离的进程。我们用 postgres 作为示例服务。

假设我们在 container 中运行 postgres。
Postgres 会为持有的每个连接生成一个进程，因此同一个 postgres 实例的所有进程都必须访问相同资源。
但我们不希望其他进程（例如 Apache）访问甚至看到 postgres 正在使用的资源（例如内存），同时也希望限制 postgres 可以消耗的资源量。

另外，我们也希望抽象每个 postgres 实例看到的 O/S 视图，让它不必关心当前运行所在 host 的具体差异。
例如 postgres 会把数据存放在 `/var/lib/postgres`，无论这台 host 上运行多少个 postgres 实例，我们都希望保持这个路径不变。

总结一下，我们希望 container 提供：
- isolation
- abstraction
- resource constraints

传统上，系统管理员使用 users 和 filesystem permissions 做隔离。
抽象通过 `chroot` 完成，资源限制通过 `rlimit` 管理。
这远远不够理想，虚拟机越来越流行就说明了这一点。
为了让事情更容易管理，我们希望 kernel 提供一种机制来实现上面的目标。

不幸的是，Linux 中不存在这样一个单一机制。
相反，我们有一些彼此独立的机制，可以把它们编排在一起，实现不同程度的 isolation、abstraction 和 resource constraints。
这些机制包括：
- namespaces
- cgroups
- chroot/pivot_root
- seccomp
- appaprmor/SELinux

因此，“Linux container”并不是一个定义严格的实体。
从 kernel 的角度看，并不存在 container 这种东西，只有一组带着 namespaces、cgroups 等机制运行的 processes。

要理解这些机制如何工作，最好先回顾相关 Linux primitives 的工作方式：
- [Processes](prep-processes.md)
- [Users](prep-users.md)
- [Mounts](prep-mounts.md)
- [chroot/pivot_root](prep-chroot.md)
- [Memory management](prep-memory.md)

看完这些 primitives 后，再来看新机制如何工作：
- [Namespaces](prep-namespaces.md)
- [cgroups](prep-cgroups.md)
- [seccomp](prep-seccomp.md)
- [capabilities](prep-capabilities.md)
