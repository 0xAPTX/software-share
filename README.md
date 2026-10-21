# APTX 软件仓库

公开的软件分享目录。安装包保存在 **GitHub Releases**，GitHub Pages 提供目录与固定下载入口，无需登录即可下载。

- 软件目录：<https://0xaptx.github.io/software-share/>
- iTunes 自动下载入口：<https://0xaptx.github.io/software-share/download/itunes/>
- VMware Fusion 自动下载入口：<https://0xaptx.github.io/software-share/download/vmware-fusion/>
- Claude iOS 自动下载入口：<https://0xaptx.github.io/software-share/download/claude-ios/>
- 全部文件与版本：<https://github.com/0xAPTX/software-share/releases>

专属下载页会尝试自动开始下载，并保留「立即下载」按钮；浏览器也可能要求用户点击确认。

## 已收录

| 软件 | 版本 | 平台 | 文件大小 |
| --- | --- | --- | --- |
| iTunes | 12.6.3.6 | Windows x64 | 270,075,208 字节（257.6 MiB） |
| VMware Fusion | 13.6.4 / 24832108 | macOS 13.0+，Intel / Apple Silicon | 556,702,913 字节（530.9 MiB） |
| Claude | 1.261019.20 / 39361214947 | iPhone / iPad，最低 iOS 18.0 | 175,946,422 字节（167.8 MiB） |

文件由仓库维护者提供，上传时不修改文件内容。iTunes 的原文件名标注为 12.6.5.3，但内部文件版本和产品版本均为 12.6.3.6，页面按内部版本标注。VMware Fusion 的版本、构建号和最低系统版本读取自映像内应用元数据，通用架构已通过可执行文件头确认。Claude 的版本、构建号、最低系统和设备类型读取自 IPA 内的应用元数据。IPA 需要通过适用的签名或安装方式使用，网页下载不会直接安装应用。旧版软件请自行确认与你的设备及系统兼容。

文件 SHA-256：

- iTunes：`fc1af1adeb31b4dc3ba8c3b68a5b329d4dc5b21f3c8c251fd72b1f31bd0116e6`
- VMware Fusion：`a43fd031165896bc1b7ecc61eb07b377bfc01b014c9111b08e18a6a1af121191`
- Claude iOS：`09739f2ee6122040800c6e7b6d7098d0ffe673c312548b0ebc21c9e76532869e`

## 以后如何添加软件

1. 打开仓库的 **Releases → Draft a new release**。
2. 新建一个版本标签，例如 `toolname-1.0.0`，填写标题与说明。
3. 上传安装包，等附件上传完成后点击 **Publish release**。
4. Actions 自动读取已公开的附件，生成目录与每个文件的下载页并部署到 Pages。

新附件默认用文件名展示，自动生成专属下载链接。点击网站的「复制分享链接」即可分享。草稿和预发布版本不会显示。

如需友好名称、固定短链接、中文说明或准确版本号，在 `software.json` 的 `items` 中新增配置：

```json
{
  "release": "toolname-1.0.0",
  "asset": "ToolSetup.exe",
  "slug": "toolname",
  "name": "软件名称",
  "version": "1.0.0",
  "platform": "Windows · 64 位",
  "category": "实用工具",
  "description": "用途与特点。"
}
```

其中 `release`、`asset` 必须与 Release 标签及附件名完全一致。`slug` 只允许小写英文字母、数字和连字符，在整个目录中唯一，对应 `/download/toolname/`。每个版本使用不同的标签；需要固定入口指向新版时，将同一个 slug 移到新版配置。

如果在已发布的 Release 中补传或删除附件，请手动运行 **Actions → Publish software downloads → Run workflow** 刷新目录。删除或编辑 Release 以及推送代码也会触发更新。下载次数可在 GitHub Release 中查看。

## 本地预览

依赖 Python 3.9+ 与已登录的 GitHub CLI，无需 npm 或付费 API。

```sh
gh api --paginate --slurp repos/0xAPTX/software-share/releases > releases.json
python3 -m unittest discover -s tests -v
python3 scripts/build.py --releases releases.json
python3 -m http.server 8080 --directory dist
```

构建会检查附件归属及 SHA-256（GitHub 返回摘要时与配置核对）。安装包不进入 Git 提交历史；新增软件无需新增 Secrets。GitHub Pages 的下载入口最终跳转到 GitHub Releases，访问者需要能连接 GitHub 的下载服务。

Release 事件会触发 `main` 上的发布工作流，避免 Pages 的 [Release 标签部署旧产物问题](https://github.com/actions/deploy-pages/issues/383)。部署后还会读取线上 `build-info.json` 核对任务编号，确认当前版本已经实际生效。
