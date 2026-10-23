# 安卓：GKD 自动点击跳过

GKD 与 Clash / Mihomo 分别工作：前者通过无障碍执行界面点击，后者负责网络分流。不能把小火箭模块直接导入 GKD；广告也可能先出现再被跳过。

1. 按 [GKD 官方指引](https://gkd.li/guide/)选择当前发布渠道安装。
2. 理解无障碍可以读取界面并执行操作后，按官方步骤授权。
3. 从 [Lin-arm 社区订阅](https://github.com/Lin-arm/GKD_subscription)的 README 获取当前入口，初次只开启目标应用的开屏规则，避免重复订阅。
4. 重开应用，分别检查跳过效果和正常功能；后台失效时查 [官方 FAQ](https://gkd.li/guide/faq)。

误点时关闭对应规则，完全停止时关闭 GKD 无障碍。无需因此重设节点或安装 HTTPS 解密证书。

本项目尚未完成安卓真机验收。GKD 程序与第三方订阅的作者 / 许可分别见 [署名](../THIRD_PARTY_NOTICES.md)，本仓库不提供 APK、规则镜像或截图。
