# Linux processes

_process_ 是一个操作系统概念，用来描述拥有独立内存空间和资源的任务。
在 Linux 中，_processes_ 通过 `clone()` system call 创建；它会克隆一个已有 process 来创建新的 process。
`clone()` 调用接收多种 flags，用来告诉 Linux 哪些资源要和原 process 共享，哪些资源要复制。
通常我们不会直接使用 `clone()` system call；而是使用 POSIX 调用（例如 `fork()`），这些调用在 _glibc_（userspace）中实现。
事实上，我们使用的大多数 Linux 和 POSIX 接口都实现于 _glibc_，而不是 kernel。

我们熟悉的 `fork()` 调用会通过带上一组 flags 调用 `clone()` 来创建一个 _process_。Threads 则通过 `pthread_create()` 调用创建。

在底层，threads 和 processes 都是 tasks，并由一个叫做 *task_struct* 的 struct 表示（并不意外）。*task_struct* 大约有 170 个字段，大小约 1k。一些值得注意的字段包括：_*user_、_pid_、_tgid_、_*files_、_*fs_、_*nsproxy_。
- *fs_struct* _*fs_ 保存当前 root、working directory、umask 等信息。
- *pid* struct 会把 processes 映射到一个或多个 tasks。

## Processes - fork 与 exec

传统上，\*nix 系统按顺序调用以下调用来创建新 processes：
 1. *fork()* - 复制当前 process，VM 使用 copy-on-write。
 1. *exec()* - 用新的 program image 替换 text/data/bss/stack。

调用 *exec()* 之后，新的 process image 会从 entrypoint（main function）开始执行，并接收新的命令行参数（argv）。

- glibc 的 *fork()* 和 *pthread_create()* 都会调用 clone() syscall。
- *clone()* 会基于 parent 创建新的 *task_struct*。
- 通过 flags 控制资源共享（例如共享 VM、共享/复制 fd）。
