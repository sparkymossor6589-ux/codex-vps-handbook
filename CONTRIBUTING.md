# 反馈与贡献

反馈请附：系统 / 客户端 / 配置版本、网络环境、复现步骤、预期与实际结果，以及必要的脱敏证据。[问题模板](.github/ISSUE_TEMPLATE/bug_report.md)

改动请说明原因、来源许可、验证范围和回退办法。不要提交真实凭据、私人链接、数据库、证书或原始手机日志。

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 tests/test_meter.py
node tests/test_bili_feed_safe.js
python3 tools/check_public.py .
```

服务测试使用临时文件和回环端口。提交前另查敏感内容、Git 历史和提交身份；设备结果单独记录。新增第三方内容需保留作者与许可，见 [许可范围](LICENSE_SCOPE.md)。
