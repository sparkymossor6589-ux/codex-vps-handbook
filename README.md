# Codex VPS 实战手册

用 Codex 搭建和维护个人 VPS 的实操笔记，涵盖分流、在线更新、多设备接入和应用广告排查。

## 当前状态

| 部分 | 进展 |
|---|---|
| 服务器与分流 | Xray 基础连接、在线配置和分流维护；当前分流 v5 |
| 视频直连 | Dailymotion 两个公开样本在 Mac 通过，完整观看和手机待测 |
| 应用广告 | 更新至 r39：修复知乎阅读路径误拦，测试三条裸 IP 目标拦截；手机阅读与广告效果待确认 |
| 安卓 | 接入配置和 GKD 路线已整理，真机待测 |

[详细测试状态](docs/09-validation.md) · [变更记录](CHANGELOG.md)

## 开始使用

[准备](docs/00-quickstart.md) → [部署](docs/02-server-setup.md) → [分流](docs/03-routing-and-clients.md) → [在线更新](docs/04-online-updates-and-traffic.md)

[故障案例](docs/05-real-world-fixes.md) · [应用去广告](docs/06-adblocking.md) · [维护与回退](docs/07-maintenance-and-rollback.md) · [安卓 GKD](docs/15-android-gkd.md)

[项目经过](docs/10-project-story.md) · [Codex 提示词](docs/08-prompts.md) · [参考代码与测试](src/README.md)

示例参数需要自行填写，不提供可用节点或完整第三方模块。

## 来源与许可

基于 Xray、Mihomo 和上游客户端 / 规则整理。本地维护代码与第三方内容分别授权。

[项目贡献](CONTRIBUTIONS.md) · [第三方署名](THIRD_PARTY_NOTICES.md) · [许可范围](LICENSE_SCOPE.md) · [反馈与贡献](CONTRIBUTING.md) · [私密材料](SECURITY.md)
