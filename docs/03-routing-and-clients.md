# 分流与设备接入

| 对象 | 用途 |
|---|---|
| 节点订阅 | 连接参数与估算流量 |
| 分流配置 | DNS、策略组和访问规则 |
| 接入网页 | 引导导入；网页地址不能直接当订阅地址 |

## 规则顺序

局域网 / 保留地址 → 精确个人例外 → 指定服务 → 公共规则与国内地址兜底 → 最终策略。窄范围下载子域放在整站后缀前。

Mac / iPhone 使用 Shadowrocket 配置路由。更新后核对“实际使用”标记及策略组选中的节点，再看规则命中并操作真实业务。

[Shadowrocket 示例](../examples/shadowrocket.conf.example)使用 `VPS` 策略组和 `My VPS` 节点，需替换成自己的参数。

安卓使用 [Mihomo 示例](../examples/mihomo.yaml.example)，不能直接套用小火箭语法。[字段文档](https://wiki.metacubex.one/config/proxies/vless/)

项目已整理安卓统一入口并做解析检查，真机接入仍待验证。各设备状态见 [验证状态](09-validation.md)。
