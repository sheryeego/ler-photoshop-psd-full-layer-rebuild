# ler-photoshop-psd-full-layer-rebuild

**在 Windows 上，用 Adobe Photoshop 或 PhotoCraft 把参考图重建为可编辑分层 PSD。** 当前技能版本：**1.1.0**。本仓库为私有分发。

这是一套供 Codex 使用的工作流、参考文档和自动化脚本。它要求完整主体、完整背景、原生文字、内嵌智能对象和适用的独立光影，并验证 PSD 保存后能真实编辑。

PNG／JPG 没有可恢复的原始图层；本技能指导素材重建与必要补绘。主体默认使用完整素材参与构图，外部蒙版控制显示范围，移开主要对象后背景应连贯。补绘、字体替代和内部未继续拆分的范围须说明。

## 1. 私下分发方式

- **私下提供安装 ZIP**：仓库所有者把完整技能安装包交给指定接收者，接收者按下文手动安装，无需获得仓库权限。
- **私下提供仓库链接**：接收者须登录已获仓库访问权限的 GitHub 账号；仅收到链接并不能下载私有仓库。

个人账号私有仓库的协作者权限包含写入。仅想提供下载时，可优先私下发送安装 ZIP，无需添加仓库协作者。权限规则见 [GitHub 官方说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/permission-levels-for-a-personal-account-repository)。技能包不附带仓库访问凭据。

## 2. 使用前准备

| 项目 | 要求 |
|---|---|
| 操作系统 | Windows；其他系统不在本版验证范围内。 |
| Codex | 能读取本地 `SKILL.md` 技能，并能在获得授权后执行本地文件操作和脚本。 |
| Photoshop 路线 | 自备 Windows Adobe Photoshop，先打开应用。桥接使用 COM＋JSX，默认连接 Photoshop 2026／主版本 27；其他版本先核实 ProgID 和版本。 |
| PhotoCraft 路线 | 自备含 `photocraft-cli.exe` 的 PhotoCraft；本版以 CLI **0.5.0** 实测。提供自己的 CLI 绝对路径。 |
| Python | PhotoCraft 适配器和命令行安装示例需要 Python **3.10＋**；适配器只使用标准库。仅使用 Photoshop 桥接时不需要该适配器。 |
| 素材 | 提供参考图及可取得的原素材、Logo、字体；需要补绘时，当前 Codex 环境须有实际可用的图像生成／编辑工具。 |

技能不附带 Photoshop、PhotoCraft、字体、模型或账号，也不会自动安装这些软件。原生文字会使用本机实际存在的字体。

## 3. 安装技能

完整技能在仓库的 **`ler-photoshop-psd-full-layer-rebuild/` 子目录**。安装时保留整个文件夹，不能只复制 `SKILL.md`。

### 方法 A：手动安装 ZIP（私下分发推荐）

1. 收到所有者私下提供的技能 ZIP 后，先核对随包 SHA-256。若已获仓库访问权限，也可登录 GitHub，在本仓库主页点击 **Code → Download ZIP**。
2. 解压到新目录，找到直接包含 `SKILL.md` 的 **`ler-photoshop-psd-full-layer-rebuild`** 文件夹。GitHub 仓库 ZIP 还有一层仓库外壳，要进入外层才能找到技能子目录。
3. 选择自己的 Codex skills 目录。默认是 `%USERPROFILE%\.codex\skills`；设置了 `CODEX_HOME` 时为 `%CODEX_HOME%\skills`。
4. 已有同名技能时，先把旧版完整备份到 skills 扫描目录之外，再复制整个新技能文件夹。不要合并两个版本。
5. 安装后的入口应为 `<自己的 skills 目录>\ler-photoshop-psd-full-layer-rebuild\SKILL.md`。在 Codex 下一轮输入技能名称使用。

不要把整个仓库外层文件夹当作技能安装，也不要把自动化脚本单独复制到别处。

### 方法 B：让 Codex 从 GitHub 安装

先确认当前 GitHub 账号已获该私有仓库的访问权限，并在本机完成正常登录或配置可用的 Git 凭据。把下面这段话粘贴到 Codex：

```text
使用 $skill-installer，从这个私有 GitHub 仓库安装技能：
https://github.com/sheryeego/ler-photoshop-psd-full-layer-rebuild
仓库内技能目录：ler-photoshop-psd-full-layer-rebuild
分支：main
使用我本机已有且获授权的 GitHub 访问方式，不显示或写入令牌。
安装前告诉我准确安装位置，允许我选择自己的位置。
如果已存在同名技能，先说明版本、备份旧版，再完整替换，不混合文件。
安装后核对 SKILL.md、agents、assets、references 和 scripts 都已安装。
```

确认 Codex 给出的目标位置后再批准安装。通常为 `%USERPROFILE%\.codex\skills\ler-photoshop-psd-full-layer-rebuild`；配置了 `CODEX_HOME` 时使用其 `skills` 子目录。访问失败或没有仓库权限时，使用方法 A；不要把访问令牌粘贴进聊天或 README。

### 方法 C：命令行安装

适合已有 Python、Git、Codex、内置 `skill-installer`，且本机 Git 凭据能访问该私有仓库的使用者。在 PowerShell 执行：

```powershell
$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
$installer = Join-Path $codexRoot 'skills\.system\skill-installer\scripts\install-skill-from-github.py'
python -X utf8 $installer --repo sheryeego/ler-photoshop-psd-full-layer-rebuild --ref main --path ler-photoshop-psd-full-layer-rebuild --method git
```

该命令使用安装器的默认目标目录。自定义目录可追加 `--dest '<自己的 Codex skills 目录>'`，该目录应是 Codex 实际读取的位置。没有安装器脚本时使用方法 A 或 B。安装器遇到同名目标目录会停止；更新前先备份，不用删除命令强行覆盖。

## 4. 使用：Windows＋PhotoCraft

附上参考图，把下面的提示词交给 Codex。方括号内容替换为自己的信息：

```text
使用 $ler-photoshop-psd-full-layer-rebuild，把这张参考图重建为可编辑分层 PSD。
执行软件：Windows＋PhotoCraft。
PhotoCraft CLI 路径：[自己的 photocraft-cli.exe 绝对路径]。
画布：[沿用原图尺寸，或填写目标尺寸]。
要求完整主体、完整背景、原生文字和内嵌素材，使用外部蒙版控制构图。
按需要独立编辑的对象分层，说明内部没有继续拆分的范围。
补绘部分、字体替代和与参考图的差异要记录。
完成最终 PSD 保存重开、改字、移动、内嵌源完整性、背景和图层复合验证。
成品保存到：[自己的成品目录]，另建任务子目录。
只交付我需要的 PSD、预览和中文编辑说明；测试副本、脚本及日志留在工作区。
```

CLI 路径应指向 **`photocraft-cli.exe`**，不是桌面应用快捷方式。路径有空格也可以使用，不需要沿用作者的安装目录。

可先做只读连接检查，示例路径须替换为自己的路径：

```powershell
$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
$skillRoot = Join-Path $codexRoot 'skills\ler-photoshop-psd-full-layer-rebuild'
$photoCraftCli = 'E:\Apps\PhotoCraft\photocraft-cli.exe'
python -X utf8 (Join-Path $skillRoot 'scripts\photocraft_runner.py') --cli $photoCraftCli probe
```

成功时返回 CLI 版本和路径。该检查不启动桌面应用，不创建常驻服务。也可通过 `PHOTOCRAFT_CLI` 或 PATH 配置 CLI 路径。

## 5. 使用：Windows＋Adobe Photoshop

先打开 Photoshop，再附上参考图并输入：

```text
使用 $ler-photoshop-psd-full-layer-rebuild，把这张参考图重建为可编辑分层 PSD。
执行软件：Windows＋Adobe Photoshop。
先检查我的 Photoshop 版本和可用的自动化连接。
要求完整主体、完整背景、原生文字和内嵌智能对象，并按独立编辑需求分层。
保留原图与旧版，不覆盖我尚未保存的文档。
补绘、字体替代和未继续拆分的范围要写入中文说明。
在实际 Photoshop 中完成最终 PSD 保存重开、改字、移动、背景和素材完整性验收。
成品保存到：[自己的成品目录]，另建任务子目录。
交付 PSD、预览和中文编辑说明；制作记录与测试副本留在工作区。
```

只读桥接检查：

```powershell
$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
$skillRoot = Join-Path $codexRoot 'skills\ler-photoshop-psd-full-layer-rebuild'
& (Join-Path $skillRoot 'scripts\Invoke-Photoshop.ps1') -ProbeOnly
```

默认 ProgID 为 `Photoshop.Application.200`，预期主版本为 27。其他版本先核实，再按 [Photoshop 自动化说明](ler-photoshop-psd-full-layer-rebuild/references/photoshop-automation.md) 显式传入参数；不自动改注册表或重启应用。

## 6. 如何判断结果可用

- 文字仍是原生文字层，并能改字后保存重开。
- 智能对象内是完整源素材；关闭构图蒙版后可检查被隐藏的内容。
- 移开主要对象后背景连贯，没有空洞或原主体残片。
- 适用的阴影、光效和装饰能独立调整；无法可靠分离的内在材质光照有范围说明。
- 最终 PSD 在目标软件中真实重开并完成编辑测试；仅有图层数量或成功保存日志不够。

**PhotoCraft 验收通过不代表 Photoshop 已验收。** 如果最终用 Photoshop 编辑 PhotoCraft 制作的 PSD，请增加：“必须在我的 Photoshop 中完成真实重开与编辑验收。”未执行的软件检查必须写明 `not_run`。

## 7. 本版测试范围

PhotoCraft CLI 0.5.0 的独立几何样例通过 12 项结构和真实编辑检查，包括中英文文字、形状、完整透明内嵌源、分组、外部固定蒙版、主体移动、图层复合、PSD 重开和预览像素一致性；另检查中文路径、分批执行和已有成品防覆盖。

Photoshop 桥接与检查脚本保持原样，并做了静态检查；**1.1.0 更新未在 Photoshop 中执行原生重开测试**。几何样例验证编辑通路，不代表任意客户参考图已经完成或能精确还原。

可选的 `scripts/smoke_photocraft.py` 使用 PhotoCraft 生成结构样例，像素校验额外需要 Pillow。缺少 Pillow 时不会自动安装；它不是正常 CLI 组装的必需依赖。命令和范围见 [PhotoCraft 自动化说明](ler-photoshop-psd-full-layer-rebuild/references/photocraft-automation.md)。

## 8. 常见问题

| 现象 | 处理 |
|---|---|
| 私有仓库链接显示 404／无法下载 | 核对账号访问权限和登录状态，或向所有者取得私下提供的安装 ZIP。 |
| Codex 找不到技能 | 核对安装后的 `SKILL.md` 路径，保留完整文件夹；下一轮输入完整技能名称。 |
| 同名目录已存在 | 检查旧版并先完整备份到 skills 扫描目录之外，再更新；不要混合文件。 |
| 找不到 PhotoCraft CLI | 提供真实的 `photocraft-cli.exe` 路径，或配置 `PHOTOCRAFT_CLI`／PATH。 |
| Photoshop 连接失败 | 先确认应用已打开，核对实际版本、ProgID 和预期主版本。 |
| 字体缺失 | 提供已安装字体或确认替代字体，记录外观差异。 |
| 宿主阻止脚本或文件访问 | 核对准确路径、操作范围与授权；不关闭系统保护或修改系统策略。 |
| 期待恢复原始设计图层 | PNG／JPG 只能重建；提供原始设计文件和素材才能保留其原有结构。 |

## 文件导航

```text
README.md
CHANGELOG.md
ler-photoshop-psd-full-layer-rebuild/
  SKILL.md
  agents/openai.yaml
  assets/
  references/
  scripts/
```

[技能入口](ler-photoshop-psd-full-layer-rebuild/SKILL.md) · [PhotoCraft 自动化](ler-photoshop-psd-full-layer-rebuild/references/photocraft-automation.md) · [Photoshop 自动化](ler-photoshop-psd-full-layer-rebuild/references/photoshop-automation.md) · [原生验收](ler-photoshop-psd-full-layer-rebuild/references/native-validation.md) · [更新记录](CHANGELOG.md)
