# AWS 赠金、预算与准备

先确认费用，再创建实例。本攻略的起点是用 AWS 100 美元赠金覆盖一年个人 VPS 的基础开销。

## 100 美元赠金怎么用

截至 2026-10-25，AWS 为符合资格的新用户提供 100 美元注册赠金，完成指定活动还可获得额外赠金。本例预算只按最初的 100 美元计算。[AWS 计划说明](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html)

AWS 的两个期限需要分清：

| 项目 | 含义 |
|---|---|
| Free plan | 最长六个月，或赠金先用完时结束；不会自动提供十二个月运行时间 |
| Free Tier 赠金 | 按当前 FAQ，通常在开户十二个月后到期；具体以自己的赠金记录为准 |
| Paid plan | 要跨过免费计划期限继续运行，需提前升级；剩余有效赠金可继续抵扣，超额或不适用赠金的用量会收费 |

[AWS Free Tier FAQ](https://aws.amazon.com/free/free-tier-faqs/) · [Lightsail 赠金适用说明](https://aws.amazon.com/free/compute/lightsail/)

在 Billing and Cost Management 中检查自己的账户计划，以及 Credits / 赠金页面的余额、到期日和适用服务。确认能抵扣 Amazon Lightsail 后，再创建实例。旧账户、其他促销赠金和不同注册条件不能直接套用本例。

## 一年的预算

本例选择带公网 IPv4 的 Linux/Unix 入门套餐：0.5 GB 内存、2 vCPU、20 GB SSD、每月 1 TB 流量，标价 5 美元 / 月。[Lightsail 定价](https://aws.amazon.com/lightsail/pricing/)

```text
基础实例费：5 美元 × 12 个月 = 约 60 美元
赠金预算：100 美元
理论余量：约 40 美元，且仍受赠金到期日限制
```

这个估算假设只保留一台同价实例，符合赠金抵扣条件，并在有效期内运行。额外快照、存储、超额流量等另计；客户端购买、域名等独立费用不包含在内。余额再多，也不能延长赠金有效期。

创建预算提醒，定期看账单和赠金余额。**预算提醒不会自动停机或封顶费用。** 不再使用时，备份后删除不需要的计费资源；普通 Lightsail 实例关机后仍会计费。[计费说明](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-frequently-asked-questions-faq-billing-and-account-management.html)

## 部署前准备

- AWS 账户、可用赠金和自己确认的套餐；保存计划结束及赠金到期提醒。
- 目标设备与客户端、常用业务清单；准备分别测试 Wi-Fi 和蜂窝网络。
- 自己的 SSH 密钥与私人配置目录；已有节点先备份，再改动。

本例使用 Ubuntu + Xray（VLESS / REALITY / Vision），由客户端提供代理连接；设备是否接管全部流量取决于客户端模式与分流配置。Codex 可协助检查环境、修改配置和排错，使用模板见[工具附录](08-prompts.md)。

下一步：[创建服务器并部署](02-server-setup.md)。
