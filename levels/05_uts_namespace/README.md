# Level 05: UTS namespace

UTS namespace 允许每个 container 拥有自己的 hostname。
进入新的 UTS namespace 后，你可以修改 hostname，而不会影响整台机器的 hostname。

使用 `linux` 模块提供的 [sethostname()](https://rawgit.com/Fewbytes/rubber-docker/master/docs/linux/index.html#linux.sethostname) 调用。

## 如何检查你的成果

container 内部的 hostname 应该不同于外部。
具体来说，我们希望 hostname 是 container ID。

```
$ sudo python rd.py run -i ubuntu /bin/bash -- -c hostname
0c96ccc-ee60-11e5-b7ff-600308a39608
11196 exited with status 0
$ hostname -f
vagrant-willy-amd64
```
