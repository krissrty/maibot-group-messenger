# 麦麦跨聊天群消息工具 📨

让麦麦在私聊中接到指令后，真正去指定QQ群发送普通文字。

> 麦麦，去群号123456789，跟大家说声晚安。
>
> 麦麦，去“姐妹群”向大家道个歉。

## 功能

- `list_message_groups`：查询机器人已经加入的QQ群及群号。
- `send_group_message`：按群号或群名发送1–4000字普通文本。
- 群名匹配到多个群时返回候选，不擅自选择。
- 使用文本消息段，不把文字里的CQ代码解释为指令。
- 根据适配器回执报告结果；没有有效消息ID时不报告成功，不自动重发。

## 使用说明

机器人必须已经加入目标群；群禁言、账号限制等仍会影响发送。
插件通过适配器公开API发送，不会补写麦麦目标群的聊天上下文。
没有额外的主人白名单，能使用该工具的范围取决于麦麦现有聊天及工具权限。
本插件使用SnowLuma适配器API；通过该适配器连接NapCat的兼容性尚未实测。

## 环境要求

- MaiBot 1.2.5 及以上的 1.x 版本，maibot-plugin-sdk 2.6.x–2.x。
- 已安装并连接 [SnowLuma 适配器](https://github.com/Mai-with-u/MaiBot-SnowLuma-Adapter)，插件 ID 为 `maibot-team.snowluma-adapter`。
- 这是第三方插件，不会自动安装或配置适配器。声明的兼容范围不代表每个版本组合均经过实测。

## 安装

1. 点击本仓库 **Code → Download ZIP**，解压。
2. 将包含 `plugin.py` 和 `_manifest.json` 的文件夹放进麦麦的 `plugins/maibot-group-messenger/`，避免多套一层目录。
3. 重启麦麦，在插件管理中确认“跨聊天群消息工具”加载成功。
4. 需要自定义时，将 `config.example.toml` 复制为 `config.toml` 后修改；不要覆盖已有配置。

插件 ID：`krissrty.group-messenger`。本地旧版 `local.*` 插件用户应停用旧版后再安装，避免同名工具重复。

## 测试

使用麦麦自带的 Python（需包含 maibot_sdk），在仓库目录运行：

```console
python -m unittest discover -s tests
```

测试使用模拟接口，不会真实发送QQ消息或发表说说。测试通过不代表当前QQ账号的实际接口可用。

## 反馈与许可

问题请提交 [Issues](https://github.com/krissrty/maibot-group-messenger/issues)，附麦麦/SDK/适配器版本和脱敏日志，勿上传Token、完整配置或聊天数据库。

[MIT License](LICENSE)。
