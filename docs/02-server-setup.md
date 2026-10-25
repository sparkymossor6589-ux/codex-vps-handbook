# 创建服务器并部署 Xray

本例为 AWS Lightsail 东京、Ubuntu、Xray（VLESS / REALITY / Vision）。先完成[赠金与预算核对](01-start-with-codex.md)。

## 1. 创建实例

在 Lightsail 创建 Linux/Unix 实例，选择 Ubuntu 和符合预算的套餐。本例为 5 美元 / 月、带公网 IPv4 的入门套餐；创建前再核对控制台价格、架构和流量额度。

配置自己的 SSH 密钥。需要固定地址时，将静态 IPv4 关联到实例；保存登录信息到私人目录。检查端口占用，防火墙只开放所需服务，SSH 尽量限制为自己的来源地址。

## 2. 部署连接服务

使用仓库的 [bootstrap_xray.py](../src/bootstrap_xray.py) 前，先在目标服务器检查 Ubuntu、x86_64、systemd、`ubuntu` 用户与端口条件。它适用于新部署，已有服务先备份并核对路径。[执行条件](../src/README.md)

```sh
python3 src/bootstrap_xray.py
```

默认只显示说明。按提示核对官方 Xray 版本和包的 SHA-256，准备自己的服务器地址与已验证的 REALITY 目标，再明确使用 `--apply` 执行部署。程序会生成连接参数并写入受限文件；部署后检查配置、服务状态与日志。

也可使用 [Xray 上游安装项目](https://github.com/XTLS/Xray-install)，不要混用两套服务路径。

## 3. 导入自己的客户端

按[服务端样例](../examples/xray-server.json.example)与客户端字段匹配 UUID、公钥、short ID 和 server name。REALITY 私钥只留服务器，SSH 私钥留在登录设备；两者用途不同。[REALITY 文档](https://xtls.github.io/config/transports/reality.html)

选中节点，检查目标网站的可信 HTTPS 和实际业务。手机分别测试 Wi-Fi / 蜂窝；服务已启动或延迟测试通过，还需继续确认实际联网。

下一步：[分流与设备接入](03-routing-and-clients.md)。
