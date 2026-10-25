# 阅读路线

从 AWS 赠金和费用开始，先搭通连接，再完善分流、维护与广告屏蔽。

| 步骤 | 要做什么 | 完成标志 |
|---|---|---|
| 1. [赠金与准备](01-start-with-codex.md) | 核对资格、到期日、套餐与预算提醒 | 能算清一年基础费用及额外开销 |
| 2. [搭建服务器](02-server-setup.md) | 创建 Ubuntu 实例，部署固定版本 Xray | 服务运行，自己的客户端实际联网 |
| 3. [分流与设备](03-routing-and-clients.md) | 按设备导入节点和规则，检查实际出口 | 常用业务正常，Wi-Fi / 蜂窝分别通过 |
| 4. [在线更新](04-online-updates-and-traffic.md) | 设置私人 HTTPS 入口和版本化资源 | 客户端能更新，失败能[回退](07-maintenance-and-rollback.md) |
| 5. [广告屏蔽](06-adblocking.md) | 按应用启用模块并检查正常功能 | 同时确认广告变化与阅读、评论、播放 |

已有节点可直接从第 3 步开始。遇到问题先查[故障案例](05-real-world-fixes.md)，安卓另看 [GKD](15-android-gkd.md)。

真实节点、密钥和入口地址保存在自己的私人目录；示例中的 `REPLACE_WITH_...` 需要替换。服务器检查、客户端命中与设备使用结果分别确认，当前进度见[测试状态](09-validation.md)。

[搭建经过](10-project-story.md) · [参考代码](../src/README.md) · [Codex 辅助模板](08-prompts.md)
