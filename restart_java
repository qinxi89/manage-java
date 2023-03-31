#!/usr/bin/env python
# -*- coding: utf-8 -*-
# time: 2023/3/30 11:07
# file: test.py
# author: qinxi
# email: 1023495336@qq.com
import os
import re
import shutil
import subprocess
import time

pid = '7004'
pro = 'admin-api'
jvm_opt = '-server -Xms512M -Xmx512M -Xmn256M'
Active = 'dev'

source_path = f'/data/package/{pro}'
target_path = f'/data/{pro}'
log_path = f'/data/logs/{pro}.log'

# 检查目录是否存在，如果不存在则创建目录
if not os.path.exists(source_path):
    os.makedirs(source_path)
if not os.path.exists(target_path):
    os.makedirs(target_path)
if not os.path.exists(os.path.dirname(log_path)):
    os.makedirs(os.path.dirname(log_path))


def find_jar(path) -> str:
    """查找最新的 jar 包文件"""
    files = os.listdir(path)
    files = [f for f in files if f.startswith(pro) and f.endswith('.jar')]
    if not files:
        raise ValueError(f"No jar files found in {path}")
        exit('No jar files found')
    files.sort(reverse=True)
    full_path = os.path.join(path, files[0])
    return full_path,files[0]    # 返回类似('/data/package/admin-api/admin-api-1.0-SNAPSHOT.jar', 'admin-api-1.0-SNAPSHOT.jar') 的元组

def is_service_up() -> bool:
    """检查服务是否在运行"""
    cmd = f'netstat -ntpl | grep {pid}'
    output = subprocess.getoutput(cmd)
    return str(pid) in output


def stop_service():
    """停止服务"""
    java_pid = subprocess.getoutput(f'netstat -ntpl | grep {pid} | awk "{{print $NF}}" | awk -F"/" "{{print $1}}"')
    if not java_pid:
        print('Service is already down.')
    else:
        pro_pid = re.search(r'(\d+)/java', java_pid).group(1)  # 匹配进程号
        print('Service is up,Stopping program, current program process number is: ',pro_pid)
        os.kill(int(pro_pid), 15)
        os.kill(int(pro_pid), 9)


def start_service(jar_path: str):
    """启动服务"""
    print(f'Starting service with {jar_path}...')
    with open(log_path, 'w') as f:
        print(f'cd {target_path} && java {jvm_opt} -Dspring.profiles.active={Active} -jar {jar_path}')
        subprocess.Popen(f'cd {target_path} && java {jvm_opt} -Dspring.profiles.active={Active} -jar {jar_path}',
                         stdout=f, stderr=f, shell=True, start_new_session=True)

def main():
    """主程序"""
    try:
        # 1、查找将要部署的jar 包是否存在
        source_jar = find_jar(source_path)

        # 2、判断/data/packeage/{pro}目录上是否存在jar包, 不存在则提示“安装包不存在”，并退出程序
        if not source_jar:
            print(f'{source_path} No jar file found.')
            return

        # 3、检查备份文件是否存在
        if os.path.isfile(target_path + '/' + source_jar[1]):
            # 备份JAR包
            shutil.move(target_path + '/' + source_jar[1], target_path + '/' + source_jar[1] + '.bak')
        else:
            print(target_path + '/' + source_jar[1] + ' not found... skip...')

        # 4、移动/data/package/{pro}目录上的jar包到/data/{pro}
        shutil.move(source_jar[0], target_path)

        # 5、备份/data/{pro}/{jar} 为/data/{pro}/{jar}.bak
        target_jar = find_jar(target_path)

        # 6、查询服务pid，查询不到，提示服务没有在运行，则启动服务；查询到则执行停止服务，然后启动服务
        if is_service_up():
            # 停止当前正在运行的服务
            stop_service()
            time.sleep(6)
            print('Start restarting the service.....')
            # 启动jar包
            start_service(target_jar[1])
            time.sleep(30)

            # 等待40s后，查询服务是否在运行，不存在，再等20s，回滚；存在则提示启动成功
            if not is_service_up():
                print('No pid found, please wait for 20 seconds......')
                time.sleep(20)

                if is_service_up():
                    print('Service started successfully.')
                else:
                    exit('No pid found,please check!')
            else:
                print('Service started successfully.')

        else:
            print('The current service is not running yet')
            start_service(target_jar[1])
            time.sleep(30)
            if is_service_up():
                print('Service started successfully.')
            else:
                exit('Service failed to start.')

    except Exception as e:
             print(f'Error occurred:{e}')
             return

if __name__ == '__main__':
    main()

