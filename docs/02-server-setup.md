# 服务器搭建：先获得一条可以验证的连接

实际项目最终采用 AWS Lightsail 东京实例、Ubuntu 和 Xray 的 VLESS + REALITY + Vision。前期也比较过其他提供商；比较和登录页面的操作不等于已经部署了对应服务器。

## 第一步：确认服务器和费用

在控制台核对地区、系统、CPU 架构、套餐、公网地址和登录方式。将真实地址、SSH 私钥和连接凭据保存到私人目录。

项目中的历史方案使用每月 5 美元基础套餐。本文不承诺当前价格、优惠或流量额度；购买时以自己账户的报价为准。[Lightsail 官方计费说明](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-frequently-asked-questions-faq-billing-and-account-management.html)可用于核对计费方式。

预算提醒有通知延迟，不能当作达到阈值就立即停止费用的开关。[AWS Budgets 官方说明](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html)明确提到费用产生与收到通知之间可能存在延迟。不再使用服务器时，按资源清单处理实例及相关资源；关闭浏览器页面不会删除实例。

## 第二步：检查部署环境

让 Codex 确认系统版本、架构、当前端口占用、已有服务与防火墙状态。已有服务时，先形成备份和差异说明。

实际部署程序做了以下事情：

1. 下载一个明确版本的官方 Xray 压缩包，并核对 SHA-256。
2. 在服务器生成独立用户标识、REALITY 密钥和 short ID。
3. 将服务端配置与客户端连接参数分别保存，限制文件访问权限。
4. 先运行配置检查，再安装并启动专用 systemd 服务。
5. 检查服务状态，将客户端参数留在私人文件中。

公开参考实现为 [bootstrap_xray.py](../src/bootstrap_xray.py)。公开版本要求使用者提供自己的版本、校验值、服务器地址和 TLS 目标，默认只显示说明，需明确 `--apply` 才执行。仅适用于说明中的新建 Ubuntu / Linux x86_64 环境，未在本次公开整理中重新部署。请先阅读 [src/README.md](../src/README.md)。

希望采用上游维护的安装路径，可先阅读 [Xray 官方安装项目](https://github.com/XTLS/Xray-install)与[官方示例](https://github.com/XTLS/Xray-examples)。不同安装路径的配置位置、服务名和用户可能不同，不能混用本项目历史服务名。

## 第三步：核对连接参数

| 参数 | 应放在哪里 |
|---|---|
| 服务器地址、端口 | 私人客户端配置 |
| 用户 UUID | 服务端与对应客户端，需要匹配 |
| REALITY 私钥 | 仅服务器 |
| REALITY 公钥、short ID、server name | 对应客户端，按服务端配置匹配 |
| SSH 私钥 | 自己的登录设备 |

[服务端配置示例](../examples/xray-server.json.example)只展示字段。`REPLACE_WITH_...` 不是可用参数；server name 与 target 也需要按自己的环境选择并验证。字段解释以 [Xray REALITY 官方文档](https://xtls.github.io/config/transports/reality.html)为准。

## 第四步：验证基础连接

- 在服务器检查配置语法、服务状态和监听端口。
- 在客户端添加自己的节点，确认选中目标节点。
- 检查可信 HTTPS 访问及实际目标业务。
- 手机分别使用 Wi-Fi 和蜂窝复测。
- 记录失败现象和实际返回，不把单次延迟测试当成业务完成。

本项目后来确认 iPhone 在 Wi-Fi 和蜂窝下可以收到 ChatGPT 文字回复；文件上传、实时语音和长时间恢复属于另行验收范围。

**示例提示词**：

```text
请检查这台服务器是否适合按当前方案部署。
先确认系统、架构、已有服务和端口，保留现有配置与回退材料。
采用明确版本和可核对来源；连接参数只保存到私人文件。
部署后分别给出服务状态、配置检查、客户端连接和实际业务的验证结果。
不要把服务器服务正常写成手机已经可以使用。
```

下一步：[分流与客户端](03-routing-and-clients.md)。
