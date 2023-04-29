import json
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import requests
import sys
LAST_CONFIG_FILE = '/你的路径/last_config.json'
CONFIG_FILE = '/etc/shadowsocks-libev/config.json'
SMTP_SERVER = 'smtp.qq.com'
SMTP_PORT = 587
SMTP_USERNAME = 'aaa@qq.com'
SMTP_PASSWORD = 'xxxxxxxx'
SENDER = 'aaa@qq.com'
RECEIVER = ['bbb@qq.com', 'ccc@qq.com']

def read_last_config():
    """
    读取上一次的配置信息并解析为字典
    """
    last_config = {}
    if os.path.exists(LAST_CONFIG_FILE):
        with open(LAST_CONFIG_FILE, 'r') as f:
            last_config = json.load(f)
    return last_config

def read_current_config():
    """
    读取当前的配置文件并解析为字典
    """
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    return config

def update_config(config, server_port):
    """
    更新配置文件中的server_port参数值
    """
    config['server_port'] = server_port
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4, separators=(',', ':'))
    print(f"已将server_port更新为{server_port}")

def check_config_changes(last_config, config):
    """
    检查配置文件中哪些参数发生了变化
    """
    changes = []
    if config['server_port'] != last_config.get('server_port', 10000):
        changes.append(('server_port', config['server_port'], last_config.get('server_port', 10000)))
    if config['password'] != last_config.get('password', 'mima'):
        changes.append(('password', config['password'], last_config.get('password', 'mima')))
    if config['method'] != last_config.get('method', 'chacha20-ietf-poly1305'):
        changes.append(('method', config['method'], last_config.get('method', 'chacha20-ietf-poly1305')))
    if config['plugin'] != last_config.get('plugin', 'v2ray-plugin'):
        changes.append(('plugin', config['plugin'], last_config.get('plugin', 'v2ray-plugin')))
    if config['plugin_opts'] != last_config.get('plugin_opts', 'server'):
        changes.append(('plugin_opts', config['plugin_opts'], last_config.get('plugin_opts', 'server')))
    return changes

def get_ip_address():
    """
    获取当前服务器的IP地址
    """
    ip_address = requests.get('https://api.ipify.org').text
    return ip_address

def send_email(subject, content):
    """
    发送邮件
    """
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = SENDER
    msg['To'] = ','.join(RECEIVER)
    
    try:
        smtp_obj = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp_obj.starttls()
        smtp_obj.login(SMTP_USERNAME, SMTP_PASSWORD)
        smtp_obj.sendmail(SENDER, RECEIVER, msg.as_string())
        smtp_obj.quit()
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败：{e}")

def restart_shadowsocks_service():
    """
    重启shadowsocks-libev服务
    """
    os.system('systemctl restart shadowsocks-libev.service')

def main():
    """
    主函数
    """
    last_config = read_last_config()
    config = read_current_config()

    server_port = int(sys.argv[1])
    update_config(config, server_port)

    changes = check_config_changes(last_config, config)

    if len(changes) > 0:
        change_info = '代理服务器更新日志，以下参数已发生变化：\n'
        for change in changes:
            change_info += f'{change[0]}: {change[2]} -> {change[1]}\n'
    else:
        change_info = '代理服务器更新日志，没有任何参数发生变化。'

    ip_address = get_ip_address()

    subject = '某某地区的服务器-Shadowsocks-libev Server Configuration Updated'
    content = f'''
代理服务器的配置已更新，请查收。

{change_info}

完整配置如下：
Server IP（服务器地址）: {ip_address}
Server Port（服务器端口）: {config["server_port"]}
Password（密码）: {config["password"]}
Method（加密）: {config["method"]}
Plugin（插件程序）: {config["plugin"]}
Plugin_Opts（插件选项）: "{config["plugin_opts"]}"
备注: 此处随意起名

其余配置保持默认即可。

By the way: 
1. 系统代理中的“PAC模式”会自动判定你访问的网站是否使用代理

2. 系统代理中的“全局模式”会对你访问的所有网站使用代理
'''

    send_email(subject, content)
    restart_shadowsocks_service()

if __name__ == '__main__':
    main()
