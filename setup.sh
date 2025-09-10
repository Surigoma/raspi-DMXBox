#!/usr/bin/bash
sudo apt update
sudo apt install libedit-dev libncurses5-dev libssl-dev libbz2-dev libffi-dev libreadline-dev liblzma-dev libsqlite3-dev

curl -LsSf https://astral.sh/uv/install.sh | sh

source ~/.local/bin/env

uv sync