# 贡献说明

欢迎改进教程、补充经过验证的设备差异和修复案例。请将改动限定到清楚的问题，并说明验证范围。

提交问题时提供系统与客户端版本、配置或模块版本、网络环境、复现步骤、预期与实际结果、相关脱敏记录。可以使用 [.github/ISSUE_TEMPLATE/bug_report.md](.github/ISSUE_TEMPLATE/bug_report.md)。

提交改动时说明触发条件、改动内容、依据、检查方式、已验证结果、待测项目和回退办法。新增第三方内容必须说明来源与许可。

不得提交真实节点、私人订阅地址、访问令牌、私钥、证书包、客户端数据库或他人个人信息。截图与日志需要人工核对；建议使用保留域名和明确的占位符。

本地检查：

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 tests/test_meter.py
python3 tools/check_public.py .
```

上述命令不会部署服务器；测试会在本机回环地址启动临时服务并使用临时文件。若本机策略不允许监听端口，应注明检查未执行。

设备实测请独立记录，避免把网页可访问、语法解析或本地测试结果扩展成手机效果。

贡献前阅读 [LICENSE_SCOPE.md](LICENSE_SCOPE.md) 和 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。请勿通过删除署名或统一添加 MIT 声明的方式处理第三方内容。
