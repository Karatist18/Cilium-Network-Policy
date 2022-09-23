#!/usr/bin/python3

import os.path
import subprocess
import os
import stat
import shutil
import hashlib
import tempfile
import pynetbox
import requests
import git
from time import sleep

nb = pynetbox.api(
    'https://test-dts-nracas.tensor.ru',
            token = ''
)
path_repo = '/home/backup_tftp/'
""" Удаляем директорию локального репо после проведения работ """
def remove_dir():
    remove_dir = subprocess.Popen(f'rm -drf {path_repo}', shell = True)
    
""" Запрос на создания merge-request """
def merge():
    API_KEY = ''
    headers = {'content-type': 'application/json','PRIVATE-TOKEN': API_KEY}
    data = {"id":"'3'", "source_branch":"'fix'","target_branch":"'master'", "title":"'fix'"}
    res = requests.post("https://adm-git.tensor.ru/api/v4/projects/718/merge_requests", data='{"id":"3", "source_branch":"fix","target_branch":"master", "title":"fix"}', headers=headers)
    res
    telebot()
    
def telebot():
    res = requests.get("https://api.telegram.org/bot[token]/sendMessage?chat_id=-1001567707361&text=New merge in repo network")
    res
check_file = os.path.exists(f'{path_repo}network.yaml')

""" Api запрос к netbox """

network_array = list()
prefix = nb.ipam.prefixes.filter(tag='test_container')

""" Программа, которая атомарно пишет в файл локального репо, и при наличии изменений в целевом файле записывает его в ветку fix, делает коммит и создаёт mergee """

def diff_csv(temp): 
    with open(temp,'rb') as t:
        temps = hashlib.md5()
        while True:
            data = t.read(8192)
            if not data:
                break
            temps.update(data)
    try:
        with open(f'{path_repo}network.yaml', 'rb') as c:
            csv = hashlib.md5()
            while True:
                data = c.read(8192)
                if not data:
                    break
                csv.update(data)
        return bool(temps.hexdigest() == csv.hexdigest())

    except FileNotFoundError:
        return False

def copy_with_metadata(source, target):
    shutil.copy2(source, target)
    st = os.stat(source)
    os.chown(target, st[stat.ST_UID], st[stat.ST_GID])

def atomic_write(target_file):
    temp_file = tempfile.NamedTemporaryFile(
    delete=False,
    dir=os.path.dirname(target_file))
    try:
        if os.path.exists(target_file):
            copy_with_metadata(target_file, temp_file.name)

        with open(temp_file.name,'w') as f:
            for net in network_array:
                f.write(f'- {net}' + '\n')
                f.flush()
                os.fsync(f.fileno())

        if diff_csv(temp_file.name) == True:
            print("Нет изменений")
            remove_dir()

        else:
            print("Есть изменения")
            os.replace(temp_file.name, target_file)
            repo.index.add(items=['/home/backup_tftp/network.yaml'])
            repo.index.commit('write a line into test.file')
            remote = repo.remote()
            remote.push()
            merge()
            remove_dir()
            
    finally:
        if os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass
            
check_file = os.path.exists(f'{path_repo}')
if check_file:
    remove_dir()
    sleep(5)
    repo = git.Repo.clone_from(url='git@adm-git.tensor.ru:dts/backuper/backup_tftp.git', to_path='../home/backup_tftp',b='fix')
else:
    repo = git.Repo.clone_from(url='git@adm-git.tensor.ru:dts/backuper/backup_tftp.git', to_path='../home/backup_tftp',b='fix')

for net in prefix:
    network_array.append(net)
atomic_write(f'{path_repo}network.yaml')