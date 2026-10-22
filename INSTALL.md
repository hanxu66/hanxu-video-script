# 安装、更新与排错

## 让Codex安装

```text
请用 $skill-installer 从 https://github.com/hanxu66/hanxu-video-script/tree/v0.1.0/skills/hanxu-video-script 安装韩叙短视频口播写稿Skill，技能名 hanxu-video-script。请识别我的系统，保留SKILL.md、references、agents和LICENSE。已有同名旧版时，先将旧版备份到技能发现目录之外，再更新，不改其他技能和用户材料。告诉我实际安装路径，并检查是否能够识别及读取。
```

安装目标是仓库中的技能子目录，不能把源码仓库根目录误当技能。以安装器报告的实际位置为准，不要再往另一目录重复安装。如果本次对话还看不到新技能，在后续对话重试，仍未出现再重开Codex。

## 手动安装

1. 打开[最新Release](https://github.com/hanxu66/hanxu-video-script/releases/latest)，下载`hanxu-video-script-v0.1.0.zip`及可选的同名`.sha256`校验文件。GitHub自动生成的“Source code”是开发源码，目录层级不同。
2. 解压得到`hanxu-video-script`文件夹，核对以下结构，保留整个目录。
3. 复制到本机技能发现目录。按[OpenAI官方文档](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)，用户级目录是`$HOME/.agents/skills`。

```text
hanxu-video-script/
  SKILL.md
  README.md
  INSTALL.md
  USAGE.md
  LICENSE
  agents/openai.yaml
  references/angle.md
  references/structure.md
  references/verbatim.md
  references/revision.md
  references/quality.md
  references/output.md
```

| 系统 | 正确技能入口 |
|---|---|
| macOS | `~/.agents/skills/hanxu-video-script/SKILL.md` |
| Windows | `%USERPROFILE%\.agents\skills\hanxu-video-script\SKILL.md` |

Mac可在Finder“前往文件夹”输入`~/.agents/skills`，Windows可在文件资源管理器地址栏输入`%USERPROFILE%\.agents\skills`；目录不存在时可创建。不要只复制`SKILL.md`，不要多嵌套一层同名目录。内置安装器若使用它报告的其他受支持位置，不需为匹配表格重复复制。

从GitHub“Code → Download ZIP”下载时，技能位于`hanxu-video-script-main/skills/hanxu-video-script`，复制其中的整个子目录。发布ZIP额外包含用户说明，源码中的技能子目录和发布ZIP的核心技能文件一致；两种方式都能运行。

## 验证安装

```text
使用 $hanxu-video-script，确认你已经读到本Skill及它的相对引用，告诉我它的版本和输入方式。我要用自己的材料写口播，不读取其他项目，也不安装其他业务Skill。接下来我会讲一段真实经历，请只问会改变写稿判断的必要问题。
```

只识别名字不等于实际写稿成功；请接着完成[第一次写稿](USAGE.md)。核心写稿无需联网、Python、API密钥或剪辑软件。只需助手能读取这套技能文件和你的材料；文件保存是可选功能。

## 更新和常见问题

| 情况 | 处理 |
|---|---|
| 看不到技能 | 核对实际安装位置和层级，在后续对话重试，仍未出现再重开Codex。 |
| 两份同名技能 | 保留一个有效安装，把旧版备份移出所有技能发现目录。 |
| 安装目标已存在 | 先核对并备份旧版再更新，不直接删除或强行覆盖用户资料。 |
| 提示缺内部选题库、客户库或其他业务Skill | 本包无需这些依赖；让助手从本包入口重新读取，只使用你提供的材料。 |
| 没有文件写入能力 | 直接在对话交付完整稿和可复制续接摘要，不影响写稿。 |
| 文章链接读不到 | 粘贴可用全文；不能仅凭标题或摘要假装完成改编。 |
| 稿子不像自己说话 | 给一段自己的原话或修改稿，指出具体哪句不自然，再按该处改稿。 |
| 想写的只有题名 | 让助手围绕一次具体经历追问；不要让它编你的客户和结果。 |

技能安装目录只放方法文件。稿件、原始材料和反馈放在你自己的工作目录，如Mac的`~/Documents/我的口播稿`或Windows的`D:\内容创作\我的口播稿`。更新仅替换技能，不覆盖工作目录。没有主动上传或同步功能。

安装机制与目录参考[OpenAI官方技能文档](https://learn.chatgpt.com/docs/build-skills)。其他客户端的技能目录、文件权限和调用方式以该客户端为准，不作全客户端兼容承诺。
