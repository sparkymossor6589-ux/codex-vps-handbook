# 配置示例

这些文件展示字段与分离方式，没有可用连接参数，不能原样连接服务器。`example.invalid` 是保留的无效示例域名；所有 `REPLACE_WITH_...` 都需按自己的配置替换。

| 文件 | 用途 |
|---|---|
| xray-server.json.example | 服务端字段结构；完整部署还需用户、服务、防火墙与路由限制 |
| shadowrocket.conf.example | 极简分流示例，绑定自己添加的 `My VPS` 节点 |
| mihomo.yaml.example | Mihomo 节点字段与极简规则；DNS 策略需另行设计 |
| traffic-config.json.example | 私人 HTTPS 接入服务参数 |
| android-registry.json.example | 可选安卓授权表结构 |
| adblock-module.srmodule.example | 独立模块结构，无真实应用处理能力 |

将需要的示例复制到自己的私人目录后再填写参数；修改后的真实文件不提交到本仓库。示例中的 1 TiB 是展示用的本地估算配额，不是套餐承诺。

启用安卓服务时，在私人接入配置增加 `android_registry` 指向自己的授权表，准备 `root/shared/Tokyo-Android.yaml` 和所选官方客户端安装包。若只需要基础订阅与分流，不填写安卓项。

启用应用资源服务时，按 src/README.md 准备自己审查并有权分发的版本目录与哈希清单。没有准备对应资源时不要展示为“去广告已可用”。

## 署名与许可

Xray 样例按 CC BY-SA 4.0 提供，来源和改动见 [许可说明](xray-server.json.example.license)。其余文件的授权见 [LICENSE_SCOPE.md](../LICENSE_SCOPE.md)。
