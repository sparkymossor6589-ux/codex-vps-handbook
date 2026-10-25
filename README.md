# 自搭一年免费VPS（VPN），附带广告屏蔽

利用 AWS 新用户的 100 美元赠金，搭建个人 VPS，完成设备连接、分流、在线维护，再按需加入广告屏蔽。

我最初的想法很简单：用这笔赠金覆盖一年的服务器费用，搭一套自己能管理、出问题能修、更新能回退的个人网络环境。这篇攻略记录具体做法和踩过的坑，Codex 是搭建和维护时用到的辅助工具。

## 一年免费的前提

本例采用 AWS Lightsail 东京的 5 美元 / 月 Linux 套餐，基础实例费按一年约 **60 美元**估算，低于 100 美元赠金。

**“一年免费”是赠金覆盖首年云资源费用的目标，尚非运行满一年的实测结果。** 赠金资格、余额、适用服务和到期日以账户为准；额外资源、超额流量及不适用赠金的费用另算。AWS Free plan 最长六个月，要继续运行需升级 Paid plan，超出赠金后会按量收费。[赠金条件与预算](docs/01-start-with-codex.md)

## 按顺序搭建

1. [核对赠金、套餐和预算](docs/01-start-with-codex.md)
2. [创建服务器并部署 Xray](docs/02-server-setup.md)
3. [连接设备并设置分流](docs/03-routing-and-clients.md)
4. [配置在线更新与流量显示](docs/04-online-updates-and-traffic.md)，做好[日常维护和回退](docs/07-maintenance-and-rollback.md)
5. 基础连接稳定后，再按需设置[应用广告屏蔽](docs/06-adblocking.md)；安卓另见 [GKD](docs/15-android-gkd.md)

已有节点可从[阅读路线](docs/00-quickstart.md)选择章节。[故障案例](docs/05-real-world-fixes.md) · [搭建经过](docs/10-project-story.md) · [参考代码](src/README.md) · [Codex 辅助模板](docs/08-prompts.md)

## 当前进展

| 部分 | 状态 |
|---|---|
| 连接与分流 | Mac 基础连接可用，iPhone Wi-Fi / 蜂窝文字对话获确认；分流 v5 |
| 视频直连 | Dailymotion 两个公开样本在 Mac 通过，完整观看和手机待测 |
| 广告屏蔽 | r39 包含阅读路径修复和三条裸 IP 目标拦截试验；手机阅读与广告效果待确认 |
| 安卓 | 接入配置和 GKD 路线已整理，真机待测 |

广告屏蔽需要客户端规则或模块配合，单独搭建 VPS 不会自动去除应用广告。[详细测试状态](docs/09-validation.md) · [广告排查](docs/14-adblock-followup.md) · [变更记录](CHANGELOG.md)

## 来源与许可

本攻略基于 Xray、Mihomo、客户端及上游规则整理，公开脱敏示例和部分本地维护代码；示例参数需自行填写。

[本地整理与改动](CONTRIBUTIONS.md) · [第三方署名](THIRD_PARTY_NOTICES.md) · [许可范围](LICENSE_SCOPE.md) · [反馈与贡献](CONTRIBUTING.md) · [敏感信息说明](SECURITY.md)
