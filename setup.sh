#!/usr/bin/bash
sudo apt update
sudo apt install libedit-dev libncurses5-dev libssl-dev libbz2-dev libffi-dev libreadline-dev liblzma-dev libsqlite3-dev

curl https://pyenv.run | bash

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

source ~/.bashrc

pyenv update
pyenv install $(cat ./.python-version)