# 服务器搭建

本项目使用 Ubuntu + Xray（VLESS / REALITY / Vision），实例位于 AWS Lightsail 东京。

## 部署步骤

1. 核对地区、架构、费用、公网地址、SSH 登录及已有服务。价格和计费以自己的控制台为准，预算提醒不是费用上限。[AWS 计费说明](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-frequently-asked-questions-faq-billing-and-account-management.html)
2. 保存备份，检查端口、防火墙与系统环境。
3. 选择官方 Xray 版本，核对下载包 SHA-256；在服务器生成 UUID、REALITY 密钥与 short ID。
4. 分别保存服务端配置与客户端参数，限制权限。先检查配置，再启动服务。
5. 客户端导入并选中节点，检查可信 HTTPS 和目标业务；手机分别测 Wi-Fi / 蜂窝。

## 参考实现

[bootstrap_xray.py](../src/bootstrap_xray.py) 默认只显示说明，需明确 `--apply` 才部署。它要求自己提供版本、校验值、服务器地址和 TLS 目标；适用条件及执行影响见 [源码说明](../src/README.md)。已有部署不会被直接覆盖。

也可使用 [Xray 上游安装项目](https://github.com/XTLS/Xray-install)，但不要混用两套服务路径。

[配置样例](../examples/xray-server.json.example)只展示字段。REALITY 私钥仅留服务器，公钥、short ID、UUID 与 server name 按两端配置匹配；SSH 私钥留在登录设备。[REALITY 文档](https://xtls.github.io/config/transports/reality.html)

下一步：[分流与设备接入](03-routing-and-clients.md)。
