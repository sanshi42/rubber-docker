# Level 04：overlay CoW filesystem

到目前为止，每次都解压 image 很慢，而我们希望 containers 可以快速启动。
另外，如果每个 container 不占用这么多空间也会更好（以 ubuntu minimal 为例，大约 180MB）。

在这个 level 中，我们会添加 overlayfs。
额外的好处是：因为新的 root 会成为 mountpoint，现在可以让 `pivot_root()` 工作了！

我们要做的是把 image 解压到 *image_root* 目录（如果尚未解压），然后创建以下内容：
- 一个 *container_dir*，其中包含 overlayfs 的 mount 目录
- 一个 writable branch 目录（*upperdir*）
- 一个 *workdir* 目录

## 练习

实现这一步之后，尝试几件事来观察 overlayfs 的行为：
- 在 container 中使用 `dd` 写入一个文件，看看是否能填满 host drive。
- 往 image 目录写入一个大文件（比如 1GB），然后在 container 中以非截断写入方式打开它，可以试试这段 Python 代码：`open('big_file', 'r+')`。open 操作耗时多久？为什么？
- 在 container 中做一些文件操作（写文件、移动文件、删除文件），然后查看 `upperdir`（使用 `ls -la`）。

## 相关文档

- [OverlayFS - Kernel archives](https://www.kernel.org/doc/Documentation/filesystems/overlayfs.txt)

## 如何检查你的成果

```
$ time sudo python rd.py run -i ubuntu /bin/bash -- -c true
为 container 创建了新的 root fs：/workshop/containers/7a3393a1-df94-4c44-a935-700ec52c2607/rootfs
11191 exited with status 0

real	0m3.475s
user	0m1.492s
sys	0m1.260s

$ time sudo python rd.py run -i ubuntu /bin/bash -- -c true
为 container 创建了新的 root fs：/workshop/containers/98282744-82bd-4c70-bbf9-028e8c92f995/rootfs
11196 exited with status 0

real	0m0.162s
user	0m0.088s
sys	0m0.032s
```
注意，使用同一个 image 第二次启动 container 几乎不花时间，因为我们不需要再次解压 image。
