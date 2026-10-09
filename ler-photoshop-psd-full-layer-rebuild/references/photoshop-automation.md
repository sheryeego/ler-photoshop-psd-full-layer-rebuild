# Photoshop 原生自动化

## 使用前检查

适用于真正创建、修改或检查 PSD 的任务。脚本在 Windows PowerShell / PowerShell 7 下通过 COM 附着到已经运行的 Photoshop；不安装软件，不创建 MCP 服务。

```powershell
& '<skill目录>\scripts\Invoke-Photoshop.ps1' -ProbeOnly
& '<skill目录>\scripts\Invoke-Photoshop.ps1' -ScriptPath '<任务目录>\build.jsx'
& '<skill目录>\scripts\Invoke-Photoshop.ps1' -ScriptPath '<skill目录>\scripts\Inspect-ActiveDocument.jsx' -ResultPath '<任务目录>\layer-inventory.json'
```

替换为实际绝对路径。ResultPath 不覆盖已有文件，父目录需已存在。

默认映射为 Photoshop 2026、主版本 27、ProgID Photoshop.Application.200。这是本机已验证配置，并非对每个安装环境的保证。-ExpectedApplicationPath 可进一步约束路径。其它版本先只读核实注册项，再显式传入 -ProgId 和 -ExpectedMajorVersion。

-ProbeOnly 返回路径、版本和文档数量，不执行 JSX。没有运行实例时报告错误，不静默回退到通用 Photoshop.Application、2025 或另一个进程。COM sandbox 权限不足时走工具的准确动作审批，不改系统策略。

制作 PSD 的授权一般覆盖本次新文档编辑，不覆盖丢弃其它未保存文档。修改型脚本必须绑定自己的新文档或准确授权文档。连接脚本不会判断自定义 JSX 的业务安全性。

## 编写 JSX 时的经验

- 使用 ExtendScript 可支持的语法；文件读写显式设 File.encoding = 'UTF8'。不要将现代 JavaScript 语法直接交给旧解释器。
- 先检查 app.documents.length 再取 app.activeDocument。用准确文档引用；在 try/finally 恢复修改过的 rulerUnits、displayDialogs 和原活动文档。
- 按任务创建布局数据和构图脚本，不复制历史海报的固定坐标、像素阈值、素材路径、字体或图层数量作为通用构建器。
- newPlacedLayer、placedLayerEditContents 等 Action Manager 操作需要目标版本实测。对位透明素材时参考完整源画布和 smartObjectMore.transform，不只看可见像素边界。
- 保留完整源内容，使用外部构图蒙版。棋盘格图案不是透明背景，需要检查实际 alpha。置入时明确分辨率、尺寸、变换与坐标。
- 字体显示名称可能与真实样式不同。核对 textItem.font 和 Action Manager 字体/样式字段，视觉比对字重。缺字体时按授权处理替代，不自动安装。
- 不透明度可能量化到 255 个步长；目标 50 的编辑验证可允许 ±0.3 数值容差，不能放宽肉眼可见错误。
- 编辑测试恢复文字内容可能触发重新排版。对副本测试，优先恢复历史状态或重新打开未修改副本，不保存测试改动。
- COM/JSX 超时或结果不明确时，先检查目标文档与输出，不立即重放可能已生效的修改。

## 检测范围

智能对象 linked 状态无法读取时标记 unknown 并继续核对；顶层统计不能证明嵌套对象没有外链，需要进入每种实际使用的源检查。

Inspect-ActiveDocument.jsx 只读取当前文档、图层类型、父组可见性、文字字体、智能对象信息、图层复合和读取错误。它不切换复合、不打开文件、不进入智能对象、不改变活动图层，属于结构初检。effectivelyVisible 只表示图层和父组的眼睛状态，未计算蒙版、画布裁切、不透明度、遮挡或混合结果。

## MCP 替代路径

已有 Photoshop MCP 时先枚举它真正支持的工具，并以服务返回的路径/版本验证目标。能力不足时说明限制，或在授权内用已验证 COM/JSX 补足。不能因为 MCP 支持保存，就认定它支持完整文字、嵌入、蒙版和复合操作。

连接切换和软件安装是单独配置任务。本 skill 不携带注册表修改脚本，也不自动重启服务。
