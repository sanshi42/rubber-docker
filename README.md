#  从零开发一个迷你 Docker

## 预备内容

[预备内容](https://docs.google.com/presentation/d/10vFQfEUvpf7qYyksNqiy-bAxcy-bvF0OnUElCOtTTRc/edit?usp=sharing) 涵盖本次研讨会所需的所有基础知识，包括：

- Linux 系统调用及 glibc 封装

- chroot 与 pivot_root
- 命名空间（namespaces）
- 控制组（cgroups）
- 内核权限（capabilities）
- 以及更多内容

## 主要内容

在每个级别的关卡进行时，请使用 [提供的幻灯片](https://github.com/Fewbytes/rubber-docker/tree/master/slides) 逐步为你的容器添加新功能。
记得阅读每一级别关卡的 README，遇到困难你始终可以在第 N+1 级别的骨架代码中找到第 N 级别的解决方案。

## linux Python 模块

并非所有必要的系统调用都暴露在 Python 标准库中。此外，我们希望保持系统调用的语义，就像用 C 语言编写一样。因此我们编写了一个名为 *linux* 的 Python 模块（查看 [linux.c](linux.c)），它暴露了相关的系统调用。更多信息请参阅 [模块文档](https://rawgit.com/Fewbytes/rubber-docker/master/docs/linux/index.html)。

## 快速开始

目前有三种方式自行开始本次研讨会：

 1. 使用一个预装所需配置和工具的公共 AMI：
    | Region | AMI |
    |--------|-----|
    | eu-central-1 | `ami-041c4af571b01d0f8` |
    | il-central-1 | `ami-036406540dcc4a690` |
    | us-east-1 | `ami-0cb446a6fd2678063` |
    | us-west-1 | `ami-0defd345b84194d79` |
 1. 我们提供了一个 [packer 模板](https://www.packer.io/) ，可用来创建你自己的 AMI。
 1. 我们有一个 [Vagrantfile](https://www.vagrantup.com/) ，可供你使用喜欢的虚拟机管理程序运行（注意：尚未完全测试）。

研讨会资料在实例的 `/workshop` 目录：
- `/workshop/rubber-docker` - 本仓库：所有操作都在这里进行
- `/workshop/images` -  容器镜像目录，已包含 Ubuntu 和 BusyBox 镜像

开始前，请先阅读 `docs` 文件夹中的准备（prep） 文档。

从 `/workshop/rubber-docker/levels/00_fork_exec`开始研讨会。

## 开发环境

如果需要构建并安装 `linux` 模块：

```sh
make install 
```

如果想生成可发布的 wheel 包：
```sh
make build
```

## 公开活动

本研讨会自 2016 年 2 月起在多个场合公开举办过：

- Opstalk meetup, Tel-Aviv, February 2016
- DevOps Sydney meetup, Sydney, June 2016
- DevOpsDays Amsterdam, Amsterdam, June 2016
- SRECon EU, Dublin, July 2016
- Sela Developer Practice, Tel-Aviv, June 2016
- SRECon US, Santa Clara, March 2018
- DevOpsDays Kiel, Kiel, May 2018

## 常见问题

### 为什么要创建这个？

因为我们认为，要真正理解某样东西，唯有从零开始亲手构建——而 Linux 容器是一个被高度炒作却很少被深入理解的技术。

### 我可以用这个仓库举办我自己的公开/私有研讨会吗？

当然可以！如果你这么做，请考虑在推特上 (@nukemberg 和 @nocoot) 通知我们，并欢迎你提交反馈。

### 本研讨会不涵盖 seccomp/用户容器/其他功能

是的，我们不可能涵盖一个真实容器引擎的全部功能。我们专注于认为对理解容器工作原理最重要的部分。

### Bug 提交

请参阅下面的“贡献”部分。

## 贡献

欢迎贡献！如果你发现了 Bug 或有改进建议，随时打开 issue 或提交 pull request。本仓库采用 MIT 许可证，你的贡献也将遵循该许可证。

## 赞助商

我们感谢 [Strigo.io](http://strigo.io/) 的支持，他们慷慨提供了平台，让我们可以专注于交付研讨会，而无需担心基础设施。
 如果你计划自己举办此研讨会，非常推荐你 [联系他们](contact@strigo.io)。
