# 从零实现 Docker 工作坊


## 预备演讲
[预备演讲](https://docs.google.com/presentation/d/10vFQfEUvpf7qYyksNqiy-bAxcy-bvF0OnUElCOtTTRc/edit?usp=sharing)
覆盖了参加这个工作坊需要的基础知识，包括：
- Linux syscalls 和 glibc wrappers
- chroot 与 pivot_root
- namespaces
- cgroups
- capabilities
- 以及更多内容

## 工作坊
推进各个 level 时，请配合使用[提供的 slides](https://github.com/Fewbytes/rubber-docker/tree/master/slides)，逐步给你的 container 增加更多功能。
记得阅读每个 level 的 readme；如果遇到困难，
总能在 level N+1 的骨架代码里找到 level N 的解法。

## linux Python 模块
Python 标准库没有暴露所有必要的 system call。
另外，我们希望保留 system call 的语义，像写 C 一样使用它们。
因此我们写了一个名为 *linux* 的 Python 模块（见 [linux.c](linux.c)），用于暴露相关 system call。
更多信息请查看[模块文档](https://rawgit.com/Fewbytes/rubber-docker/master/docs/linux/index.html)。

## 快速开始
目前有 3 种方式可以自己启动这个工作坊：
 1. 我们创建了公开 AMI，已经预装了所需配置和工具：
    | Region | AMI |
    |--------|-----|
    | eu-central-1 | `ami-041c4af571b01d0f8` |
    | il-central-1 | `ami-036406540dcc4a690` |
    | us-east-1 | `ami-0cb446a6fd2678063` |
    | us-west-1 | `ami-0defd345b84194d79` |
 1. 我们提供了一个 [packer template](https://www.packer.io/)，你可以用它创建自己的 AMI。
 1. 我们也提供了一个 [Vagrantfile](https://www.vagrantup.com/)，你可以用自己喜欢的虚拟机 hypervisor 运行它（注意：尚未充分测试）。

实例上的工作坊材料位于 `/workshop`：
- `/workshop/rubber-docker` - 本仓库，你将在这里完成所有练习
- `/workshop/images` - container images，已经包含 ubuntu 和 busybox images

开始工作坊之前，请先阅读 `docs` 目录里的准备文档。

从 `/workshop/rubber-docker/levels/00_fork_exec` 开始工作坊。

## 开发环境
如果需要构建并安装 `linux` 模块：

```sh
make install 
```

如果想生成可分发的 wheel 包：
```sh
make build
```


# PR 信息
这个工作坊自 2016 年 2 月起已经在很多地方公开举办过。

- Opstalk meetup, Tel-Aviv, February 2016
- DevOps Sydney meetup, Sydney, June 2016
- DevOpsDays Amsterdam, Amsterdam, June 2016
- SRECon EU, Dublin, July 2016
- Sela Developer Practice, Tel-Aviv, June 2016
- SRECon US, Santa Clara, March 2018
- DevOpsDays Kiel, Kiel, May 2018

# FAQ
### 为什么创建这个项目？
因为我们认为真正理解一项技术的唯一方式，是从零开始构建它；而 Linux containers 是一项热度很高却经常被误解的技术。

### 我可以用这个仓库举办自己的公开/私有工作坊吗？
当然可以！如果你这么做，欢迎在 Twitter 上告诉我们（@nukemberg 和 @nocoot），也欢迎反馈。

### 这个工作坊没有覆盖 seccomp/user containers/其他功能
是的，我们不可能覆盖真实 container engine 的完整功能集。我们尽量聚焦于理解 containers 工作原理时最重要的部分。

### 我发现了 bug！
请看下面的贡献说明。


# 贡献
欢迎贡献！如果你发现 bug 或可以改进的地方，请随时打开 issue 或 pull request。请注意，整个仓库使用 MIT license，你的贡献也将遵循该 license。

# 赞助方
感谢 [Strigo.io](http://strigo.io/) 的朋友慷慨提供平台，让我们能够交付这个以及其他工作坊，而无需担心基础设施。
如果你计划自己举办这个工作坊，我们强烈建议你[联系他们](contact@strigo.io)。
