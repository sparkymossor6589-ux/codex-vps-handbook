# 参考源码

| 文件 | 作用 |
|---|---|
| bootstrap_xray.py | 参数化 Xray 部署封装 |
| traffic_service.py | 节点 / 流量订阅与在线配置入口 |
| android_access.py + android_setup.html | 安卓授权、配置与安装包交付 |
| adblock_access.py | 白名单和哈希约束的版本化资源交付 |
| bili_feed_safe.js | 本地 r25 同步 JSON 过滤核心，移除诊断封装 |

这是选定参考实现，不是私人服务的全量镜像；真实配置、上游 bundle 和安装包不分发。[归属与许可](../CONTRIBUTIONS.md)

## 部署封装

```sh
python3 src/bootstrap_xray.py
```

默认只显示说明。执行部署需在目标服务器明确传入 `--apply --server 自己的地址 --version 已核对版本 --sha256 官方包校验值 --target 已验证主机:端口 --server-name 已验证名称`。

要求新建 Linux x86_64 / Ubuntu 环境、root、systemd、`ubuntu` 用户及可用端口。程序下载包、创建用户 / 服务、写入配置并启动连接服务，拒绝覆盖已有对应部署；失败后仍需检查已生成状态，不能假定事务自动回滚。客户端参数写入受限的 `/home/ubuntu/vps-client.json`。

## 接入服务

复制 [traffic-config.json.example](../examples/traffic-config.json.example) 到自己的私人目录，填写参数、网卡和配额并限制权限。本机测试：

```sh
python3 src/traffic_service.py --config /path/to/private/config.json --state /path/to/private/meter.json --bind 127.0.0.1 --port 18444
```

实际网卡采样依赖 Linux `/sys` 与 `/proc`。公开访问需通过 `--cert` / `--key` 设置 TLS，程序默认拒绝公开明文监听；证书续期、防火墙和安装单元需自行配置。[流量估算口径](../docs/04-online-updates-and-traffic.md)

安卓授权表由 `android_registry` 指定，交付目录为 `shared/Tokyo-Android.yaml` 与 `assets/`；准备自己的文件并核对上游许可。网页与代码的协议文件名需一致。

模块资源由 `enhance_root` 指定，每版单独存放，`current` 指向当前版。`manifest.json` 示例：

```json
{
  "version": "YYYYMMDD-rN",
  "allowed_files": ["ChineseApps.srmodule"],
  "hashes": {"ChineseApps.srmodule": "REPLACE_WITH_SHA256"}
}
```

资源必须存在、在白名单内且哈希一致。页面文案应与自己准备的模块对应；关闭入口不会撤销已导入节点或证书。

## 同步过滤核心

`bili_feed_safe.js` 需要代理脚本环境的 `$request`、`$response`、`$done`，不含完整模块和 MITM 配置。只处理选定推荐 / 开屏 JSON，保留分页和正常播放路径，不发起联网补位；异常、未知、超大或非文本响应放行。

合成测试覆盖普通 / 竖屏 / 直播内容、嵌套广告标记、空广告对象、专用开屏数组、响应头和异常放行。检查命令见 [贡献说明](../CONTRIBUTING.md)，手机结果见 [验证状态](../docs/09-validation.md)。
