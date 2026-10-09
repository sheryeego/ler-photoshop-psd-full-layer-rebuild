# ler PSD Rebuild

**让参考图片成为能够继续修改的分层 PSD。**

![参考图片与可编辑 PSD 分层示意](images/psd-layer-rebuild-demo.png)

这是一项供 Codex 使用的技能，支持 **Windows＋Adobe Photoshop** 和 **Windows＋PhotoCraft**。当前完整技能版本为 **2.0.0**；新任务未指定软件时，默认使用 Adobe Photoshop，也可以指定 PhotoCraft。

宣传图是分层示意。实际成品的可编辑范围以随附说明和实际文件验证为准。

## 可以用来做什么

- 将海报、广告或产品参考图片重建为分层 PSD，方便继续调整。
- 修改文字、移动主体、调整背景和适用的装饰效果。
- 根据需要编辑的对象安排图层，并附上中文使用说明。

PNG、JPG 本身没有原设计图层。成品属于参考重建；提供原始素材、Logo 和字体，有助于保留设计细节。补绘、字体替代与无法独立编辑的范围会在说明中注明。

## 使用前准备

- 可使用本地技能的 Codex。
- Windows 上的 Adobe Photoshop 或 PhotoCraft。
- 使用 PhotoCraft 时，准备 Python 3.10 或更高版本。
- 参考图片，以及你能提供的原素材、Logo 和字体。
- 已取得的完整技能安装包。

技能安装包不包含设计软件、字体或账号。

## 获取技能

仓库已公开。点击主页的 **Code → Download ZIP** 即可下载，无需登录 GitHub；也可以使用下方示例让 Codex 帮你安装。

下载地址：[ler-photoshop-psd-full-layer-rebuild](https://github.com/sheryeego/ler-photoshop-psd-full-layer-rebuild)。

## 安装操作

1. 将下载的 ZIP 解压到一个新目录。
2. GitHub 下载包有一层仓库外壳。进入外层目录，再找到包含 `SKILL.md` 的 **`ler-photoshop-psd-full-layer-rebuild` 子文件夹**，保留这个子文件夹内的全部文件。不要把整个仓库外层目录当作技能安装。
3. 确认安装位置。Codex 的常见位置是 `%USERPROFILE%\.codex\skills`；如果设置了 `CODEX_HOME`，则使用 `%CODEX_HOME%\skills`。自定义位置应选择 Codex 实际读取的技能目录。
4. 已有同名技能时，将旧版完整备份到技能目录之外，再放入整个新版本文件夹，避免混合两个版本。
5. 安装后检查入口为 `<技能目录>\ler-photoshop-psd-full-layer-rebuild\SKILL.md`，然后在 Codex 下一轮输入技能名称使用。

也可以让 Codex 帮你安装：

```text
使用 $skill-installer，从这个 GitHub 仓库安装技能：
https://github.com/sheryeego/ler-photoshop-psd-full-layer-rebuild
仓库内技能目录：ler-photoshop-psd-full-layer-rebuild
分支：main
安装前告诉我准确位置，并允许我选择自定义位置。
如果已有同名技能，先备份旧版，再完整替换。
```

## 使用方法

附上参考图，然后将下面的提示词交给 Codex：

```text
使用 $ler-photoshop-psd-full-layer-rebuild，把这张参考图重建为可编辑分层 PSD。
画布：沿用原图尺寸。
我需要能独立修改文字、移动主体，并调整背景和适用的装饰效果。
请完成保存、重新打开和实际编辑检查，说明补绘、字体替代及可编辑范围。
成品保存在：[我的成品目录]，另建任务子目录。
交付 PSD、预览和中文编辑说明。
```

未指定软件时使用 Adobe Photoshop。要使用 PhotoCraft，在提示词中增加：

```text
执行软件：Windows＋PhotoCraft。
PhotoCraft CLI 路径：[我的 photocraft-cli.exe 路径]。
```

如果最终需要在另一款软件中编辑，请同时写明该软件，并要求在它里面重新打开及检查成品。

## 使用时常见的问题

| 问题 | 处理 |
|---|---|
| Codex 找不到技能 | 检查文件夹名称和 `SKILL.md` 的位置；保留完整文件夹，并在下一轮输入完整技能名称。 |
| 不知道在哪里下载 | 在仓库主页选择 Code → Download ZIP；只保存介绍页或宣传图无法安装技能。 |
| 字体与参考不同 | 提供实际字体，或确认替代字体并查看成品差异。 |
| 想恢复原始设计文件 | 提供原始 PSD 和素材。只有普通图片时，只能进行参考重建。 |
| 成品要在另一款软件中使用 | 写明最终编辑软件，并要求完成实际打开与编辑检查。 |
