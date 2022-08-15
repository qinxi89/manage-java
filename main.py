#!/usr/bin/env python
# _*_ encoding:utf-8 _*_
import os
import re
import shlex
import sys
import tempfile
import time
import subprocess


# 当前文件名
_daemon = os.path.basename(__file__)

class Properties:
    """
    属性文件类
    """

    def __init__(self, file_name):

        exist_file(file_name)

        self.file_name = file_name
        self.properties = {}
        try:
            fopen = open(self.file_name, 'r')
            for line in fopen:
                line = line.strip()
                if line.find('=') > 0 and not line.startswith('#'):
                    strs = line.split('=')
                    self.properties[strs[0].strip()] = strs[1].strip()
        except Exception as e:
            raise e
        else:
            fopen.close()

    def has_key(self, key):
        if key in self.properties:
            return True

    def get(self, key, default_value=''):
        if key in self.properties:
            return self.properties[key]
        return default_value

    def put(self, key, value):
        self.properties[key] = value
        replace_property(self.file_name, key + '=.*', key + '=' + value, True)

    def get_app_home(self):
        return self.get("APP_HOME")

    def get_jar_name(self):
        return self.get("JAR_NAME")

    def get_java_home(self):
        return self.get("JAVA_HOME")

    def get_nacos_add(self):
        return self.get("NACOS_ADD")

    def get_env(self):
        return self.get("P_ACTIVE")

    def get_main_class(self):
        return self.get("MAIN_CLASS")

    def get_NACOS_ADD(self):
        if self.get("NACOS_ADD") == '':
            return " "
        else:
            return " --server.port=" + props.get("NACOS_ADD")

    def get_run_command(self):
        RUN_COMMAND = "nohup " + self.get_java_home() + " " + get_java_options() +  " -Dspring.profiles.active="+ self.get_env() + " -DNACOS_HOST=" + self.get_nacos_add() + " -jar " + self.get_app_home() + "/"+ self.get_jar_name() + " >> /dev/null 2>&1 &"
        return RUN_COMMAND

    def get_program(self):
        return self.get_app_home() + "/" + self.get_jar_name() + self.get_NACOS_ADD()

    def getProgramPid(self):
        return self.get("P_ID")

    def startProgram(self):
        p_pid = self.getProgramPid()
        if p_pid != '':
            print("The program seems to have been started pid is :%s" % p_pid)
        else:
            print('Starting program.....')
            args = shlex.split(self.get_run_command())
            print(args)
            process = subprocess.Popen(args)
            pid = process.pid
            pids= str(pid)
            self.put("P_ID", pids)
            # if os.system(self.get_run_command()) == 0:
            print('Program startup success,pid is %s:' % pid)


def stopProgram(self):
    p_pid = self.getProgramPid()
    if p_pid == '':
        print('似乎启动程序没有运行......')
    else:
        os.system('kill ' + p_pid)
        print('程序成功停止......')


def monitor(self):
    while 1:
        time.sleep(3)
        p_pid = self.getProgramPid()
        if p_pid == '':
            print('It seems this program is not running. Start it now!')
            self.startProgram()
        else:
            print('It seems this program is  running. exit!')
            exit(0)

def exist_file(file_name):
    if not os.path.exists(file_name):
        # file = open(file_name, 'rwx')
        # 关闭这个文件
        # file.close()
        # 创建一个空文件
        os.mknod(file_name)
        # 改变文件权限
        os.system("chmod 777  %s" % file_name)
    else:
        print("configuration file %s is found，Reading configuration......\n" % file_name)
        time.sleep(1)


def parse(file_name):
    return Properties(file_name)


def replace_property(file_name, from_regex, to_str, append_on_not_exists=True):
    file = tempfile.TemporaryFile(mode='w+')  # 创建临时文件

    if os.path.exists(file_name):
        r_open = open(file_name, 'r')
        pattern = re.compile(r'' + from_regex)
        found = None
        for line in r_open:  # 读取原文件
            if pattern.search(line) and not line.strip().startswith('#'):
                found = True
                line = re.sub(from_regex, to_str, line)
            file.write(line)  # 写入临时文件
        if not found and append_on_not_exists:
            file.write('\n' + to_str)
        r_open.close()
        file.seek(0)

        content = file.read()  # 读取临时文件中的所有内容

        if os.path.exists(file_name):
            os.remove(file_name)

        w_open = open(file_name, 'w')
        w_open.write(content)  # 将临时文件中的内容写入原文件
        w_open.close()

        file.close()  # 关闭临时文件，同时也会自动删掉临时文件
    else:
        print("file %s not found" % file_name)


def get_java_options():
    JAVA_OPTS = "-Xms512m -Xmx512m "
    return JAVA_OPTS


def getDaemonPid():
    """
    获取Python守护进程ID
    :return:
    """
    result,res = subprocess.getstatusoutput("ps aux | grep python3.6 \
        | grep '%s monitor' | grep -v grep | awk '{print $2}'" % _daemon)
    return result

def startDaemon():
    """
    启动Python守护进程
    :return:
    """
    d_pid = getDaemonPid()
    if d_pid != '':
        print('守护进程似乎已经启动了!')
    else:
        print('正在启动守护进程......')
        if os.system('nohup python3.6 %s monitor >> /dev/null 2>&1 &' % _daemon) == 0:
            print('守护进程启动成功,对应的进程ID是: ' + getDaemonPid())


def stopDaemon():
    """
    停止Python守护进程
    :return:
    """
    d_pid = str(getDaemonPid())
    if d_pid == '':
        print('守护进程似乎没有启动......')
    else:
        os.system('kill ' + d_pid)
        print('守护进程成功停止......')



if __name__ == '__main__':
#    _input_file_path = input('输入项目配置文件名: ')
    # file_path = 'demo.properties'
    props = Properties('spring.cfg')  # 读取文件

    # 键入启动的Java环境
    if props.has_key('JAVA_HOME'):
        if props.get('JAVA_HOME') == '':
            _input_java_home = input('输入要启动的JAVA指令目录: ')
            props.put('JAVA_HOME', _input_java_home)  # 修改/添加key=value
        else:
            print('配置文件中JAVA指令目录: %s' % props.get('JAVA_HOME'))
    else:
        _input_java_home = input('输入要启动的JAVA指令目录: ')
        props.put('JAVA_HOME', _input_java_home)  # 修改/添加key=value

    # 键入jar目录
    if props.has_key('APP_HOME'):
        if props.get('APP_HOME') == '':
            _input_app_home = input('输入要启动的jar目录: ')
            props.put('APP_HOME', _input_app_home)  # 修改/添加key=value
        else:
            print('配置文件中启动的jar目录: %s' % props.get('APP_HOME'))
    else:
        _input_app_home = input('输入要启动的jar目录: ')
        props.put('APP_HOME', _input_app_home)  # 修改/添加key=value

    # 键入启动的jar名称
    if props.has_key('JAR_NAME'):
        if props.get('JAR_NAME') == '':
            _input_jar_name = input('输入要启动的jar包名称: ')
            props.put("JAR_NAME", _input_jar_name)
        else:
            print('配置文件中启动的jar名称: %s' % props.get('JAR_NAME'))
    else:
        _input_jar_name = input('输入要启动的jar包名称: ')
        props.put("JAR_NAME", _input_jar_name)

    # 键入网站nacos地址
    if props.has_key('NACOS_ADD'):
        if props.get('NACOS_ADD') == '':
            _input_nacos_add = input('输入NACOS地址: ')
            props.put("NACOS_ADD", _input_nacos_add)
        else:
            print('配置文件中NACOS地址: %s' % props.get('NACOS_ADD'))
    else:
        _input_nacos_add = input('输入NACOS地址: ')
        props.put("NACOS_ADD", _input_nacos_add)

    # 键入网站启动环境参数
    if props.has_key('P_ACTIVE'):
        if props.get('P_ACTIVE') == '':
            _input_env = input('输入ENV: ')
            props.put("P_ACTIVE", _input_env)
        else:
            print('配置文件中环境参数名: %s\n' % props.get('P_ACTIVE'))
    else:
        _input_env = input('输入ENV: ')
        props.put("P_ACTIVE", _input_env)


    print("网站启动命令:%s\n" % props.get_run_command())

    # 键入指令
    if len(sys.argv) == 2:
        args = sys.argv[1]
    else:
        time.sleep(2)
        args = input('请输入参数命令: [ start | stop | restart | monitor ]: ')

    if args == 'start':
        props.startProgram()
        startDaemon()
    elif args == 'stop':
        stopDaemon()
        stopProgram()
        props.put('P_ID', '')  # 删除守护进程PID

    elif args == 'restart':
        stopDaemon()
        stopProgram()
        props.put('P_ID', '')  # 删除守护进程PID
        time.sleep(3)
        props.startProgram()
        startDaemon()
    elif args == 'monitor':
        monitor(props)
    else:
        print('nothing to do')
