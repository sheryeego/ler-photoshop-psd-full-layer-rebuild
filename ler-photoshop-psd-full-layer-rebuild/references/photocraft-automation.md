# Windows＋PhotoCraft 自动化

仅在本次选用 PhotoCraft 时读取。1.1.0 的实测版本是 PhotoCraft CLI 0.5.0；其他版本先检查实际命令和保存行为。安装路径由使用者提供，技能不携带应用或个人安装目录。

## 连接与批量执行

Python 3.10＋适配器仅使用标准库，执行本地 CLI，不安装依赖、不控制鼠标、不启动或重启常驻服务。

若宿主沙箱拒绝 Python 启动已经验证的 CLI，只申请该准确执行动作需要的权限；不要更改系统策略、应用配置或改用不明权限启动器。

```powershell
python '<技能目录>\scripts\photocraft_runner.py' --cli '<实际路径>\photocraft-cli.exe' probe
python '<技能目录>\scripts\photocraft_runner.py' --cli '<实际路径>\photocraft-cli.exe' commands --filter 'file.placeEmbedded'
python '<技能目录>\scripts\photocraft_runner.py' --cli '<实际路径>\photocraft-cli.exe' run --new '{"width":640,"height":480,"background":"#ffffff"}' --actions '<任务目录>\steps.json' --out '<任务目录>\new-version.psd'
python '<技能目录>\scripts\photocraft_runner.py' --cli '<实际路径>\photocraft-cli.exe' info '<任务目录>\new-version.psd' --full
python '<技能目录>\scripts\photocraft_runner.py' --cli '<实际路径>\photocraft-cli.exe' convert '<任务目录>\new-version.psd' '<任务目录>\preview.png'
```

入口接受 `--cli`；未提供时读取 `PHOTOCRAFT_CLI`，再查找 PATH。文档能力以实际运行结果为准：没有活动文档时，`commands` 的 `enabled:false` 常表示当前上下文禁用，不能只凭它认定命令不存在。

步骤 JSON 支持 `[ [命令, 参数], ... ]` 或 `{ "steps": [...] }`。大型任务可用 `{ "batches": [步骤列表, 步骤列表] }`，每个批次结束须是可以保存的完整操作单元。Windows 命令行过长时适配器在执行前拒绝；按安全边界拆批，不把创建选区和添加蒙版等事务拆开。每批保存独立 `.pcraft` 检查点，再导出最终 PSD。适配器默认拒绝覆盖已有成品，检查点在独立工作子目录。

`assets/photocraft-actions.example.json` 是可编辑文字与形状的操作样例，不是照片重建模板。示例路径与坐标仅演示 API，实际任务仍使用自己的构图数据。

本地 `run` 是受信任的文件命令，动作本身仍可读写其参数指定的文件；不能把适配器的成品防覆盖当作动作文件的权限沙箱。传入动作前检查其输入、输出路径。

MCP／`serve` 通道必须按实际版本授予工作目录能力。一些通道拒绝 `file.placeEmbedded` 等环境绝对路径命令；用户已授权本地组装时可使用官方一次性 `run` 路线，不修改权限配置绕过限制。只有需要已有实时会话时才使用它；本技能不要求新建服务。

## 组装完整图层

| 内容 | PhotoCraft 操作与注意点 |
|---|---|
| 完整透明主体／背景 | `file.placeEmbedded` 的 `path` 使用素材绝对路径；`fit:false`，显式 `scale`、`center`。保持完整源，用外部蒙版控制构图。 |
| 原生文字 | `type.create`／`type.edit`；核对字体、字号和样式。点文字 `x,y` 是基线锚点；不要按图层顶边猜位置。 |
| 色块／线条／标识 | `shape.create`，矩形、椭圆或路径；实际保存后应仍是 Shape。复杂专有标识保留原素材。 |
| 图层 ID | 从本次命令结果或 `info` 按唯一名字查找，重新打开后重新读取；不套用旧文件的 ID。 |
| 分组与顺序 | `layer.select` 的 replace/add＋`layer.groupLayers`；用 `info` 检查层树及默认视图，必要时 `layer.moveTo` 显式调整。新组的位置不能靠假定。 |
| 外部构图蒙版 | 主动 `layer.select` 目标，`select.rect`→`layer.layerMask.revealSelection`→`layer.layerMask.linked`（`linked:false`）→`select.deselect`。固定窗口内移动主体时保留未链接蒙版。 |
| 移动／变换 | 主动选目标后 `edit.transform`；例如平移矩阵 `[1,0,0,1,dx,dy]`。由实际尺寸计算坐标和比例，检查点重跑不要重复应用缩放。 |
| 图层复合 | `layerComp.new`／`layerComp.apply`／`layerComp.list`；保存前应用默认成品，并实际检查 PSD 重开后的复合。 |
| 内嵌源验证 | 重开 PSD，选智能对象，再 `layer.smartObjects.exportContents` 到新路径；对照完整源尺寸、像素和真实 alpha。有嵌套对象时继续检查内部，不以单个对象通过代表全部通过。 |

0.5.0 中部分命令的能力检查依据当前活动层，即使参数有 `layer`，也应先选中目标；已在外部蒙版和内嵌源导出中实测。没有源码素材、文字或目标能力时，报告限制而不是栅格化后称为通过。

## 保存、重开与跨软件检查

1. 从未重复变换的稳定检查点保存为新 PSD，单独导出默认预览。
2. `info` 读取最终 PSD，确认尺寸、Type／Shape／SmartObject、组、蒙版和参考组隐藏状态；读到多层只是结构检查。
3. 从 PSD 再渲染 PNG，比较解码像素及视觉。改字、移动、内嵌源导出、背景和复合检查在独立副本完成，不覆盖交付文件。
4. 移开或隐藏主体检查背景，关闭构图蒙版检查完整源；看透明边缘与局部，不以截图碎片代替完整素材。
5. 记录 `authoringApplication: PhotoCraft`、CLI 版本和通道，PhotoCraft 重开状态单列。未在 Photoshop 执行就保留 Photoshop 为 `not_run`，不能据 PhotoCraft 自身保存重开推断跨软件兼容。

技能结构样例可执行：

```powershell
python '<技能目录>\scripts\smoke_photocraft.py' --cli '<实际路径>\photocraft-cli.exe' --out-dir '<新QA目录>'
```

它用 PhotoCraft 生成独立几何素材并检查组装通路，图像读取仅用于像素验证。该检查额外需要 Pillow；缺少时报告，不自动安装。实际客户图片仍需完整重建、素材完整性、字体及视觉验收。
