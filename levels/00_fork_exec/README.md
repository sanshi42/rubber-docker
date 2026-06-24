# Level 00：fork 与 exec

在这个 level 中，我们会熟悉 `rd.py`，也就是 rubber-docker 的骨架。
`rd.py` 已经使用 *click* Python 模块实现了一个 CLI command：*run*。它的使用方式如下：

```
$ python3 rd.py run /bin/echo "Hello Docker"
```

现在这个骨架还没有真正做太多事，所以至少要让它能运行我们的可执行文件。
这可以通过 Linux 的 *fork-exec* 机制实现。

## fork-exec
在 \*nix 系列操作系统中，新 processes 通过 *fork-exec* 创建：
*fork()* 调用和 *exec()* 调用配合起来创建新的 process。

*fork()* 是 parent process 用来“分裂”自己的 system call 名称（在 Linux 中实际是 *libc* 调用），会“fork”出两个相同的 processes。
调用 *fork()* 之后，正在执行的程序会被完整复制到新的 process 中。
这个新 process（parent 的 “child”）会拥有新的 PID。
*fork()* 函数会向 parent 返回 child 的 PID，同时向 child 返回 0，以便这两个相同的 processes 能区分彼此。
从 *fork()* 调用返回后，执行会从程序中的同一位置继续，然后（通常）根据返回值走向不同分支。

有些情况下，两个 processes 会继续运行同一个 binary；但更常见的是其中一个（通常是 child）会使用 *exec()* system call（实际是一组调用）切换去运行另一个 binary executable。
当 child process 调用 *exec()* 时，原程序中的所有数据都会丢失，并被新程序的运行副本替换。

最后，parent 必须调用 *wait()*（或它的任意变体），收集 child 的 exit status，并允许系统释放与 child 相关的资源。如果没有执行 wait，已经终止的 child 会停留在 defunct（也就是 “zombie”）状态。

### 示例

```python
pid = os.fork()
if pid == 0:
    # 这里是 child
    os.execv('/bin/echo', ['/bin/echo', 'Hello Docker'])
    # 这里不可达，因为我们已经切换了 binary executable
else:
    # 这里是 parent
    waited_pid, status = os.waitpid(pid, 0) # 等待 child 结束
```

## 延伸阅读
- [os.fork()](https://docs.python.org/2/library/os.html#os.fork)
- [os.execv()](https://docs.python.org/2/library/os.html#os.execv)
- [os.waitpid()](https://docs.python.org/2/library/os.html#os.waitpid)
- Python [Lists](https://docs.python.org/2/tutorial/introduction.html#lists)
- [Wikipedia - Fork-exec](https://en.wikipedia.org/wiki/Fork%E2%80%93exec)

## 如何检查你的成果

```
$ python3 rd.py run /bin/echo "Hello Docker"
Hello Docker

3620 exited with status 0
```

## Bonus

你能否使用另一个 exec 变体来操控 child process 的环境变量（类似 [docker run -e](https://docs.docker.com/engine/reference/run/#env-environment-variables)）？
