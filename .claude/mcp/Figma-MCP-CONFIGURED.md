# Figma MCP服务器配置完成

**配置时间**: 2025-01-12 17:15
**服务器名称**: Framelink_Figma_MCP
**状态**: ✅ 配置完成

---

## 📋 配置内容

### MCP服务器信息

**名称**: `Framelink_Figma_MCP`
**类型**: Figma Developer MCP
**功能**: Figma集成,允许Claude Code与Figma设计文件交互

### 配置文件

**文件**: `d:/Claude/.mcp.json`

**内容**:
```json
{
  "mcpServers": {
    "Framelink_Figma_MCP": {
      "command": "npx",
      "args": [
        "-y",
        "figma-developer-mcp",
        "--figma-api-key",
        "YOUR_FIGMA_TOKEN_HERE",
        "--stdio"
      ]
    }
  }
}
```

---

## 🔧 配置说明

### 1. .mcp.json vs settings.json

根据Claude Code的架构,MCP服务器有两种配置方式:

**方式1: .mcp.json (推荐用于项目)**
- 位置: 项目根目录
- 文件: `.mcp.json`
- 用途: 项目级别的MCP服务器配置
- 优先级: 项目配置

**方式2: settings.json (推荐用于用户级别)**
- 位置: `~/.claude/settings.json` (用户级别)
- 字段: `pluginConfigs.[plugin-id].mcpServers`
- 用途: 用户级别或插件级别的MCP配置
- 优先级: 用户配置

### 2. 为什么选择.mcp.json

对于项目级别的MCP服务器,使用`.mcp.json`更合适:
- ✅ 简洁明了
- ✅ 易于维护
- ✅ 项目级别配置
- ✅ 不污染settings.json

---

## 🚀 使用方法

### 首次启动

**重要**: 首次启动MCP服务器时,Claude Code会提示你批准:

```
发现新的MCP服务器: Framelink_Figma_MCP

是否批准此MCP服务器?
- 类型: Figma集成
- 访问权限: Figma API

[批准] [拒绝] [查看详情]
```

**操作**: 选择"批准"

### 查看可用工具

配置完成后,可以查看Figma MCP提供的工具:

```bash
/mcp list
```

应该能看到类似:
```
Framelink_Figma_MCP:
  - mcp__Framelink_Figma_MCP__get_file
  - mcp__Framelink_Figma_MCP__get_components
  - mcp__Framelink_Figma_MCP__search_files
  ...
```

---

## 📊 Figma MCP功能

### 核心功能

1. **获取Figma文件**
   - 读取设计文件
   - 查看组件信息
   - 导出设计资源

2. **搜索设计资源**
   - 按名称搜索
   - 按类型筛选
   - 按标签过滤

3. **协作功能**
   - 评论和反馈
   - 版本控制
   - 团队协作

### 典型使用场景

**场景1: 获取设计规范**
```
从Figma获取按钮组件的样式规范
```

**场景2: 导出图标**
```
导出Figma中的所有图标为SVG/PNG
```

**场景3: 设计转代码**
```
查看Figma设计并生成对应的HTML/CSS代码
```

---

## ⚠️ 注意事项

### 1. API密钥安全

**Figma API Key**: `YOUR_FIGMA_TOKEN_HERE`

**安全建议**:
- ✅ 不要公开分享此密钥
- ✅ 定期轮换密钥
- ✅ 监控API使用情况

### 2. 权限批准

**首次使用**:
- Claude Code会弹出批准对话框
- 需要手动批准才能使用
- 批准后会记住你的选择

**撤销批准**:
```bash
/mcp remove Framelink_Figma_MCP
```

### 3. 网络要求

**需要**:
- 稳定的网络连接
- 可访问Figma API
- npm和npx可用

**检查**:
```bash
npx --version
npm --version
```

---

## 🔍 故障排除

### 问题1: MCP服务器未启动

**症状**: `/mcp list` 看不到Framelink_Figma_MCP

**解决**:
1. 检查.mcp.json是否存在: `ls -la .mcp.json`
2. 重启Claude Code
3. 查看错误日志

### 问题2: npm包安装失败

**症状**: 提示"找不到figma-developer-mcp"

**解决**:
```bash
# 手动测试安装
npx -y figma-developer-mcp --help
```

### 问题3: API密钥无效

**症状**: 提示"认证失败"

**解决**:
1. 检查API密钥是否正确
2. 访问Figma获取新密钥
3. 更新.mcp.json配置

### 问题4: 权限被拒绝

**症状**: MCP服务器启动失败

**解决**:
1. 检查settings.json中的权限配置
2. 确保允许npx命令
3. 检查防火墙设置

---

## 📝 测试步骤

### 步骤1: 验证配置

```bash
# 查看MCP配置
cat .mcp.json
```

### 步骤2: 重启Claude Code

关闭并重新启动Claude Code以加载新配置。

### 步骤3: 批准MCP服务器

首次使用时会弹出批准对话框,选择"批准"。

### 步骤4: 测试功能

```
请帮我列出Figma中的所有可用文件
```

应该能看到MCP服务器被调用并返回结果。

---

## 🎯 后续优化

### 1. 添加更多MCP服务器

可以在.mcp.json中添加更多服务器:

```json
{
  "mcpServers": {
    "Framelink_Figma_MCP": { ... },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "d:/Claude"]
    }
  }
}
```

### 2. 环境变量管理

对于敏感信息(如API密钥),可以使用环境变量:

```bash
# 设置环境变量
export Figma_API_KEY="figd_..."

# .mcp.json中使用
{
  "mcpServers": {
    "Framelink_Figma_MCP": {
      "command": "npx",
      "args": [
        "-y",
        "figma-developer-mcp",
        "--figma-api-key",
        "$Figma_API_KEY",
        "--stdio"
      ],
      "env": {
        "Figma_API_KEY": "$Figma_API_KEY"
      }
    }
  }
}
```

---

## 📚 参考资料

- [MCP官方文档](https://modelcontextprotocol.io/)
- [Claude Code MCP指南](https://code.claude.com/docs/en/mcp)
- [Figma Developer MCP](https://github.com/figma-community/figma-developer-mcp)
- [Figma API文档](https://www.figma.com/developers/api)

---

## ✅ 配置检查清单

- [x] 创建.mcp.json文件
- [x] 配置Framelink_Figma_MCP服务器
- [x] 验证JSON格式正确
- [x] 记录API密钥信息
- [x] 创建配置文档
- [ ] 首次启动并批准MCP服务器
- [ ] 测试MCP功能
- [ ] 验证与Figma的连接

---

**配置完成时间**: 2025-01-12 17:15
**配置者**: Claude (AI)
**审核者**: User (蜡烛先生)
**状态**: ✅ 配置完成,待启动测试
**下一步**: 重启Claude Code并批准MCP服务器
