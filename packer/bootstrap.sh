#!/bin/bash
set -e

function export_image() {
  image_name=$1
  export_name=$2
  shift; shift
  CONTAINER_ID=$(docker run -d $image_name "$@")
  docker wait $CONTAINER_ID
  docker export -o $export_name.tar $CONTAINER_ID
  docker rm $CONTAINER_ID
}

if [ $(id -u) -ne 0 ]; then
    echo "必须以 root 身份运行此脚本。正在尝试 sudo" 1>&2
    exec sudo -H -n bash $0 $@
fi

# 等待 cloud-init
sleep 10

# 安装 packages
export DEBIAN_FRONTEND=noninteractive
export DEBIAN_PRIORITY=critical
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# 把 repository 添加到 Apt sources：
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce stress python3-dev build-essential cmake htop ipython3 python3-pip python3-click git

# 在旧 images 上为 cgroups v1 启用 memory 和 memsw cgroups；ubuntu 24.04 cgroups v2 不需要
# sed -i.bak 's|^kernel.*$|\0 cgroup_enable=memory swapaccount=1|' /boot/grub/menu.lst
# sed -i -r 's|GRUB_CMDLINE_LINUX="(.*)"|GRUB_CMDLINE_LINUX="\1 cgroup_enable=memory swapaccount=1"|' /etc/default/grub
# update-grub

# 配置 Docker 使用 overlayfs
cat - > /etc/docker/daemon.json <<'EOF'
{
  "storage-driver": "overlay2"
}
EOF
# 重启 docker（以使用 overlay）
systemctl restart docker

usermod -G docker -a ubuntu

# 克隆 git repo
mkdir /workshop
git clone https://github.com/Fewbytes/rubber-docker.git /workshop/rubber-docker

# 拉取 images
mkdir -p /workshop/images
pushd /workshop/images
export_image ubuntu:noble ubuntu-export /bin/bash -c 'apt get update && apt get install -y python stress'
export_image busybox busybox /bin/true
cp /workshop/rubber-docker/levels/03_pivot_root/breakout.py ./
chmod +x breakout.py
tar cf ubuntu.tar breakout.py
tar Af ubuntu.tar ubuntu-export.tar
rm breakout.py ubuntu-export.tar
popd

# 启动时拉取 repo 并构建 C extension
cat > /etc/rc.local <<'EOF'
#!/bin/bash

# 允许 rc.local 在 root 拥有的目录上执行 git 命令
export HOME=/root
git config --global --add safe.directory /workshop/rubber-docker

# 拉取最新版本的 rubber-docker，安装 requirements 并构建 C extension
if [[ -d /workshop/rubber-docker ]]; then
    pushd /workshop/rubber-docker
    git pull && pip install --break-system-packages .
    # [[ -f requirements.txt ]] && pip install -r requirements.txt
    popd
fi

# 这允许我们修改 rc.local 相关内容，而无需重新生成 AMI
/workshop/rubber-docker/packer/on_boot.sh

EOF

# 设置 motd
cat > /etc/motd <<'EOF'
欢迎来到“从零实现 Docker”工作坊！

工作坊材料位于 /workshop
工作坊代码位于 /workshop/rubber-docker

提示：你可能希望以 root 身份工作。

别忘了开心地折腾和破坏东西 :)
EOF

# 设置 vim
sudo -H -u ubuntu bash -e <<'EOS'
cd ~
git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim
cp /tmp/vimrc ~/.vimrc
echo "正在使用 Vundle 安装 plugins"
echo | echo | vim +PluginInstall +qall &>/dev/null
echo "Vundle 完成"
python3 ~/.vim/bundle/YouCompleteMe/install.py 
EOS
