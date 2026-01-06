"""
Author: Brandon Arthurs
Date: 2025-12-24

##Description
This program allows a wireless slide clicker to control ProPresenter by sending API requests to a running
ProPresenter Network Interface. It enables slide transitions without requiring the ProPresenter window to be
in focus on the host PC.

Usage
1.) Ensure ProPresenter is running with its API enabled.
2.) Start this program on the host machine.
3.) Use your clicker to move forward and backward through slides

## Dependencies
This project uses several open-source libraries. Thanks to their maintainers:


- requests – HTTP library for Python ([GitHub Repo](https://github.com/psf/requests))
- psutil – Cross-platform library for system and process monitoring ([GitHub Repo](https://github.com/giampaolo/psutil))
- pynput – Library for controlling and monitoring input devices ([GitHub Repo](https://github.com/mik3y/pynput))
- keyboard – Windows-specific library for keyboard input handling ([GitHub Repo](https://github.com/boppreh/keyboard))

License MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files
(the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Copyright (c) 2025 Brandon Arthurs
"""

import time
import psutil
import socket
import requests
from pynput import keyboard
from pynput.keyboard import Key
import keyboard as win_keyboard

name = socket.gethostname()
host_ip = socket.gethostbyname(name)

"""
Using the psutil library, the program will look for the ProPresenter Helper - Network.exe. 
It will obtain the PID and find the port number assigned to the ProPresenter Network
"""
def get_port():
    while True:
        p = [process.info for process in psutil.process_iter(['pid', 'name']) if process.info['name'] == 'ProPresenter Helper - Network.exe']
        if len(p) == 0:
            time.sleep(0.2)
        else:
            pid = p[0]['pid']
            break
    while True:
        s =[connection.laddr.port for connection in psutil.net_connections(kind='inet4') if connection.pid == pid and connection.status == 'LISTEN']
        if len(s) == 0:
            time.sleep(0.2)
        else:
            port = str(s[0])
            return port

#Triggers
def next_slide():
    return requests.get(url=f'http://{host_ip}:{get_port()}' + '/v1/trigger/next')

def prev_slide():
    return requests.get(url=f'http://{host_ip}:{get_port()}' + '/v1/trigger/previous')

#Listeners
def on_press(k):
    match k:
        case Key.page_up:
            prev_slide()
        case Key.page_down:
            next_slide()


def main():
    while True:
        print(f'Network Setting\nIP address: {host_ip}\nPort: {get_port()}')
        print('======================================================================')

        """
        Listener constructor will listen for inputs from the clicker.
        """
        listener = keyboard.Listener(on_press=on_press)
        """
        Since most presenter/slide clickers are mapped to the page_up/page_down to navigate ProPresenter.
        I used the keyboard library to block these inputs from affecting other programs on the computer.
        """
        win_keyboard.block_key('page_up')
        win_keyboard.block_key('page_down')
        listener.start()
        listener.join()


if __name__ == '__main__':
    main()
