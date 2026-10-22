# 参考源码

本目录从实际项目中选择由 Codex 辅助生成 / 迭代的本地维护代码整理，未打包任何真实配置、凭据、数据库、证书、第三方脚本或安装包。代码反映这次个人部署的实现方式，公开整理没有在新机器上复现整套部署。

## 文件与改动

| 文件 | 职责 | 本次公开整理 |
|---|---|---|
| bootstrap_xray.py | 历史固定版本的 Xray 部署 | 改为显式入口，默认仅说明；增加平台 / root 检查，统一为个人服务名 |
| traffic_service.py | 节点 / 流量订阅、在线配置与入口调度 | 使用通用节点显示名，修正页面中的环境专属描述 |
| android_access.py + android_setup.html | 授权接入、配置与安装包交付 | 保留原路径兼容和页面逻辑，不含授权表 / 安装包 |
| adblock_access.py | 受保护的版本化资源交付 | 保留白名单与哈希检查，不含应用运行资源 |

这几个接入服务文件以同一目录的普通模块相互导入，使用 Python 标准库。测试采用 `PYTHONPATH=src`，测试数据都是本地合成数据。

## 部署程序的适用条件

`bootstrap_xray.py` 根据原项目部署封装整理为参数化示例，不携带实际服务器采用的固定版本、校验值或 TLS 目标。使用者需自行选择并核对官方版本及压缩包 SHA-256，再填入自己的目标与 server name。程序使用 systemd、useradd、Linux x86_64 与 ubuntu 用户等环境约定，需在自己的服务器逐项核对。

默认执行只显示说明：

```sh
python3 src/bootstrap_xray.py
```

明确部署时需要先审阅源码、核对官方发布包、确认 `ubuntu` 用户存在、443 端口可用、防火墙设置正确。然后才可在目标服务器以 root 执行 `--apply --server 自己的地址 --version 已核对版本 --sha256 官方压缩包校验值 --target 已验证主机:端口 --server-name 已验证名称`。该操作会下载文件、创建系统用户和服务、写入配置并启动连接服务；本次预览检查没有执行它。原部署程序中的固定地址、版本、哈希与 TLS 目标已改为必填参数。

程序拒绝覆盖已存在的对应部署。预检查不能保证整个执行事务可自动回滚；失败时先检查已生成文件与服务状态，再处理。服务端私钥保留在服务器，客户端参数写入 `/home/ubuntu/vps-client.json` 并限制权限。

公共模板和上游安装方案可用于设计另一种部署路径，但不得直接混用服务路径。选择版本时同时核对包的校验值、程序路径和配置兼容性。

## 私人接入服务

先把 [traffic-config.json.example](../examples/traffic-config.json.example) 复制到自己的私人位置，填写真实字段，按目标用户设置权限。确认网卡名称；`total_bytes` 只是本地展示配额。

配置了节点 URI 和分流文件后，回环测试可使用：

```sh
python3 src/traffic_service.py --config /path/to/private/config.json --state /path/to/private/meter.json --bind 127.0.0.1 --port 18444
```

网卡读取使用 Linux `/sys` 与 `/proc`，因此实际采样在 Linux 上运行；macOS 上仅运行使用 FakeMeter 的测试。公开服务需要自己的证书、私钥、HTTPS origin 与端口；程序通过 `--cert` 和 `--key` 配置 TLS，默认拒绝公开明文监听。该目录不包含安装单元、自动续期、反向代理或云防火墙自动配置。

原计数逻辑首次采样纳入本次启动以来的累计值。只有确认初始化时间口径适合自己环境后才使用；它不是云账单。

## 可选安卓交付

在私人配置的 `android_registry` 中指定自己的授权表；结构见 examples。文件路径中的 `Tokyo-Android.yaml` 为历史交付协议名，代码与网页需要一起保持一致，不包含私人地址。

授权表的 `root` 下准备 `shared/Tokyo-Android.yaml`，以及 `assets/` 中的所选安装包。安装包通过官方来源获取并核对版本 / 哈希，不随本仓库分发。初次使用还需真实手机验收。

## 可选应用资源

设置 `enhance_root` 指向自己的资源根目录，每版使用如 `YYYYMMDD-rN/` 的目录，`current` 指向当前版本。每个版本需要 `manifest.json`：

```json
{
  "version": "YYYYMMDD-rN",
  "allowed_files": ["ChineseApps.srmodule"],
  "hashes": {"ChineseApps.srmodule": "REPLACE_WITH_SHA256"}
}
```

文件必须存在、在白名单内且哈希一致；该示例不是有效清单。`ChineseApps.srmodule` 及所需资源需由使用者按来源许可自行准备。页面介绍源于本次 14 应用的整合场景，部署者必须同步修改页面，使文案与实际准备的资源一致。

停用资源入口不会自动清除设备已经导入的节点、模块或证书。

## 本地验证

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 tests/test_meter.py
python3 tools/check_public.py .
```

测试在临时目录和回环端口检查订阅、配置、授权隔离、路径兼容、HEAD、资源白名单与哈希，以及网卡累计算法。没有执行新服务器安装或上游应用脚本。

## 来源和授权范围

本目录提供外围部署和交付实现，不包含 Xray、Mihomo 或应用去广告引擎源码。项目贡献及本轮修改见 [CONTRIBUTIONS.md](../CONTRIBUTIONS.md)，逐文件来源见 [file-provenance.json](../data/file-provenance.json)。MIT 只覆盖项目贡献者有权授权的部分，不能覆盖上游程序或未来加入的外部片段。

## r13 选定 JSON 同步过滤器

[bili_feed_safe.js](bili_feed_safe.js) 是原项目 r13 的本地兼容性处理，公开副本仅添加来源说明头。它运行于提供 `$request`、`$response`、`$done` 的代理脚本环境，不是 Node 命令行应用；不含完整模块、MITM 配置、私人诊断接收器或上游 bundle。需要按自己的客户端和许可配置请求匹配，不能单凭这个文件宣称整套模块可直接使用。

过滤器只处理选定首页 / 开屏 JSON，删除明确广告标记或指定字段，保留普通内容和分页；异常或不识别的数据放行，不发起补位网络请求。详细取舍与手机待验收状态见 [后续记录](../docs/14-adblock-followup.md)。其余 Python 接入服务仍是首次公开时选择的基础参考实现，不是私人诊断系统的全量镜像。

安装有 Node.js 的环境可运行合成回归：

```sh
node tests/test_bili_feed_safe.js
```

它检查普通 / 竖屏 / 直播内容、三种推荐路径、分页、响应头、异常 / 超大 / 非文本放行、播放路径不处理与零联网；不访问真实账号或手机。

`tools/check_public.py` 会忽略根目录 `.git` 元数据，继续检查其他源码和未跟踪文件。发布时仍需另外核对 Git 历史、文件清单及提交身份。
