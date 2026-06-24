# Users

从 kernel 的视角看，user 只是多个 structs 里的一个 `int` 参数。
一个 process（*task_struct*）有多个 uid 字段：*ruid*、*suid*、*euid*、*fsuid*。

不需要“添加”或“创建”新 users；因为 “user” 只是一个 int 参数，我们可以直接给它赋任意值。user 只有两类：
- uid 0，也就是 _root_
- 其他所有人

更多内容会在 _capabilities_ 章节说明。

用户名是 userspace 功能，kernel 完全不知道它们的存在。用户名主要由 `libnss` 和 `glibc` 实现，是从人类友好名称到 uid 数字的映射，由 `/etc/passwd` 和 `/etc/shadow` 管理。
像 `useradd` 这样的命令会操作 `/etc/passwd`、`/etc/shadow`。
如果某个 uid 在 `/etc/passwd` 中没有匹配项，除了无法映射到人类友好的名字之外，一切仍然可以工作。例如试试：

```
touch /tmp/test
sudo chown 29311 /tmp/test
ls -lh /tmp/test
```

## User permissions
kernel 使用 uid 数字（以及 gid）决定某个 process 是否允许执行特定动作。例如，如果一个 process 试图 `open()` 一个文件，kernel 会把该 process 的 *fsuid* 和文件 owner uid（以及它的 permissions mask）进行比较。

但 process 如何修改自己的 uid 字段？当 process 被 cloned 时，它会继承 parent 的 uid 字段，随后可以调用 `setuid()` 或类似接口修改 uid。只有当前 uid 为 0（root）的 process 才能修改自己的 *ruid*（real uid）。

没有 identity checks（NFS，说的就是你）。
