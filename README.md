# Codex VPS 实战手册

记录用 Codex 搭建 VPS、分流、多设备接入、在线维护和处理应用广告的过程，提供教程、脱敏示例及选定维护代码。

## 最新结果 · 2026-10-23

- **分流 v5**：新增 Dailymotion 精确媒体直连；两个公开样本在 Mac 通过，完整观看和手机待测。
- **去广告 r25**：修正推荐流过滤缺陷，补充候选素材主机拦截；Mac 检查通过，手机尚未验收，知乎切回广告未确认解决。
- 安卓接入和 GKD 仍待真机验证。[完整状态](docs/09-validation.md)

## 阅读入口

[开始](docs/00-quickstart.md) · [搭建](docs/02-server-setup.md) · [分流](docs/03-routing-and-clients.md) · [在线更新](docs/04-online-updates-and-traffic.md) · [故障案例](docs/05-real-world-fixes.md) · [去广告](docs/06-adblocking.md)

[项目经过](docs/10-project-story.md) · [Codex 提示词](docs/08-prompts.md) · [源码与测试](src/README.md) · [安卓 GKD](docs/15-android-gkd.md)

## 使用与来源

示例参数需自行填写。公开仓库不含可用节点、私人入口、证书、原始手机日志或完整第三方模块。

Xray、Mihomo、客户端和第三方规则归各自作者。本项目负责部署适配、维护与文档整理，Codex 辅助编写。[贡献边界](CONTRIBUTIONS.md) · [第三方署名](THIRD_PARTY_NOTICES.md) · [许可范围](LICENSE_SCOPE.md) · [反馈](CONTRIBUTING.md)
