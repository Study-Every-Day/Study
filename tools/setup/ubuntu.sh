#!/bin/bash
# This script is used for setup envs in ubuntu.

echo "Envs:"
echo $(which python)
echo $(python -V)
echo $(which pip)
echo $(pip -V)

echo $(which python3)
echo $(python3 -V)
echo $(which pip3)
echo $(pip3 -V)

echo "=> 安装unzip命令 ..."
sudo apt install unzip

echo "=> 下载最新的chrome浏览器 ..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

echo "=> 安装chrome浏览器 ..."
sudo dpkg -i --force-depends google-chrome-stable_current_amd64.deb
echo "=> google-chrome -version" $(google-chrome -version)

echo "=> 下载最新的chromedriver ..."
mkdir -p study/webdriver/linux/
cd study/webdriver/linux/
LATEST=$(wget -q -O - http://chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget http://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip

echo "=> 解压chromedriver ..."
unzip chromedriver_linux64.zip
cd -

echo "=> 安装第三方库 ..."
sudo apt-get install python3-setuptools
pip3 install -r requirements.txt

echo "完成!"
