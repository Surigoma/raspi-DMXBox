if [ -z $(which socat) ]; then
    echo "not found socat"
    sudo apt install socat
fi

sudo socat -d -d pty,link=/dev/vmodem0,waitslave,group-late=dialout,mode=660 tcp-l:54321