# 游戏提交页面UI设计文档

**版本**: v1.0
**创建日期**: 2025-01-12
**设计方向**: 精准实用主义 (Precise Utilitarian)
**设计师**: Claude (frontend-ui-ux skill)

---

## 目录

1. [设计方向](#设计方向)
2. [页面布局](#页面布局)
3. [设计系统](#设计系统)
4. [组件规范](#组件规范)
5. [交互设计](#交互设计)
6. [响应式设计](#响应式设计)
7. [代码实现](#代码实现)
8. [可访问性](#可访问性)

---

## 设计方向

### 美学风格：精准实用主义 (Precise Utilitarian)

**核心理念**：极致功能性，信息层级清晰，工程美感

**关键词**：
- 扁平化
- 功能主义
- 去装饰化
- 工程美学
- 精密仪器感

**ONE记忆点**：**"左侧导航锚点系统"**
- 点击导航项平滑滚动到对应区域
- 滚动时自动高亮当前区域
- 完成状态用绿色勾选标记

---

## 页面布局

### 整体结构

```
┌─────────────────────────────────────────────────────────────┐
│  顶部栏: 惊蛰 - 游戏提交              [保存草稿][预览][提交]  │
├──────────┬──────────────────────────────────────────────────┤
│          │  主内容区 (max-width: 900px)                     │
│  左侧    │                                                  │
│  导航    │  ┌────────────────────────────────────────────┐  │
│  (固定)  │  │ 步骤1: 游戏标题               必填 ✓       │  │
│          │  │ [输入框...]                                │  │
│  1. 标题✓ │  │ 5-100个字符 | 当前: 25/100 字符           │  │
│  2. 简介  │  └────────────────────────────────────────────┘  │
│  3. 正文  │                                                  │
│  4. 类型  │  ┌────────────────────────────────────────────┐  │
│  5. 媒体  │  │ 步骤2: 游戏简介               可选         │  │
│  6. 链接  │  │ [多行输入框...]                           │  │
│  7. 维度  │  └────────────────────────────────────────────┘  │
│  8. 确认  │                                                  │
│          │  (更多表单内容...)                               │
│  宽:200px │                                                  │
└──────────┴──────────────────────────────────────────────────┘
```

### 尺寸规范

| 元素 | 尺寸 |
|------|------|
| 页面总宽度 | 1440px (最大) |
| 左侧导航宽度 | 200px (固定) |
| 主内容区宽度 | 900px (最大) |
| 页面边距 | 32px |
| 卡片内边距 | 24px |
| 表单项间距 | 24px |

---

## 设计系统

### 色彩系统

采用**CSS变量**定义，便于主题切换：

```css
:root {
  /* 主色调 - 工程蓝 */
  --color-primary: #0066FF;
  --color-primary-hover: #0052CC;
  --color-primary-light: #E6F0FF;

  /* 功能色 */
  --color-success: #00A854;
  --color-warning: #FFA940;
  --color-error: #FF4D4F;

  /* 中性色 - 冷灰 */
  --color-gray-900: #1F2937;
  --color-gray-800: #374151;
  --color-gray-700: #4B5563;
  --color-gray-600: #6B7280;
  --color-gray-500: #9CA3AF;
  --color-gray-400: #D1D5DB;
  --color-gray-300: #E5E7EB;
  --color-gray-200: #F3F4F6;
  --color-gray-100: #F9FAFB;
  --color-gray-50: #FAFAFA;

  /* 背景色 */
  --color-bg-page: #FFFFFF;
  --color-bg-card: #FFFFFF;
  --color-bg-input: #FAFAFA;
  --color-bg-hover: #F3F4F6;

  /* 文字色 */
  --color-text-primary: #1F2937;
  --color-text-secondary: #4B5563;
  --color-text-tertiary: #9CA3AF;
  --color-text-placeholder: #D1D5DB;
  --color-text-error: #FF4D4F;
  --color-text-success: #00A854;

  /* 边框色 */
  --color-border-default: #E5E7EB;
  --color-border-focus: #0066FF;
  --color-border-error: #FF4D4F;
  --color-border-success: #00A854;

  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}
```

**设计理念**：
- **主色调**: 工程蓝 (#0066FF) - 专业、冷静、可信赖
- **功能色**: 简洁明了，无歧义
- **中性色**: 冷灰系列，避免暖色，保持工程感
- **无渐变**: 使用纯色，扁平化

### 字体系统

```css
:root {
  /* 字体家族 */
  --font-display: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-body: 'Inter', 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'SF Mono', 'JetBrains Mono', Consolas, monospace;

  /* 字号 */
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;
  --font-size-2xl: 24px;
  --font-size-3xl: 30px;

  /* 字重 */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* 行高 */
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
}
```

**字体选择说明**：
- **Display**: SF Pro Display - 苹果系统字体，现代、清晰
- **Body**: Inter - 专为UI设计，数字友好
- **Mono**: SF Mono - 代码和标签，技术感

**避免**: Arial, Roboto (太过普通)

### 间距系统

采用**8px基准网格**：

```css
:root {
  --spacing-0: 0;
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-5: 20px;
  --spacing-6: 24px;
  --spacing-8: 32px;
  --spacing-10: 40px;
  --spacing-12: 48px;
  --spacing-16: 64px;
  --spacing-20: 80px;
}
```

### 圆角系统

```css
:root {
  --radius-none: 0;
  --radius-sm: 4px;
  --radius-base: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;
}
```

---

## 组件规范

### 1. 顶部栏 (Top Bar)

**结构**：
```
┌─────────────────────────────────────────────────────────────┐
│  ← 返回         惊蛰 - 游戏提交           [保存草稿][预览][提交] │
└─────────────────────────────────────────────────────────────┘
```

**样式规范**：
- **高度**: 56px
- **背景**: #FFFFFF
- **边框**: 底部 1px solid #E5E7EB
- **内边距**: 0 32px
- **布局**: Flexbox (space-between)

**元素样式**：
- **返回按钮**: 图标 + 文字 "返回"，左对齐
- **标题**: 字号 18px，字重 600，颜色 #1F2937
- **操作按钮组**: 右对齐，间距 12px

### 2. 左侧导航 (Side Navigation)

**结构**：
```
┌──────────────┐
│              │
│ 1. 标题    ✓ │
│ 2. 简介      │
│ 3. 正文      │
│ 4. 类型    ✓ │
│ 5. 媒体      │
│ 6. 链接      │
│ 7. 维度      │
│ 8. 确认      │
│              │
└──────────────┘
```

**样式规范**：
- **宽度**: 200px (固定)
- **背景**: #FFFFFF
- **位置**: sticky, top 80px (顶部栏高度 + 间距)
- **内边距**: 24px 0

**导航项样式**：

**默认状态**：
```css
.nav-item {
  padding: 12px 24px;
  font-size: 14px;
  color: #4B5563;
  cursor: pointer;
  transition: all 0.2s ease;
}
```

**悬停状态**：
```css
.nav-item:hover {
  color: #1F2937;
  background: #F3F4F6;
}
```

**激活状态** (当前区域)：
```css
.nav-item.active {
  color: #0066FF;
  font-weight: 600;
  border-left: 3px solid #0066FF;
  background: #E6F0FF;
}
```

**完成状态**：
- 在文字后显示绿色勾选图标 ✓
- 颜色: #00A854

### 3. 表单卡片 (Form Card)

**结构**：
```
┌────────────────────────────────────────────┐
│  1. 游戏标题                     必填 ✓   │
│                                            │
│  [输入框...]                               │
│                                            │
│  5-100个字符                               │
│  当前: 25/100 字符                         │
└────────────────────────────────────────────┘
```

**样式规范**：
```css
.form-card {
  background: #FFFFFF;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid #E5E7EB;
}
```

**标题区域**：
- **标题字号**: 16px，字重 600
- **标题颜色**: #1F2937
- **标签**: 必填/可选，12px，在标题右侧
  - 必填: #0066FF
  - 可选: #9CA3AF

### 4. 输入框 (Input)

**文本输入框**：

**默认状态**：
```css
.input {
  width: 100%;
  padding: 10px 12px;
  font-size: 14px;
  font-family: var(--font-body);
  color: #1F2937;
  background: #FAFAFA;
  border: 1px solid #E5E7EB;
  border-radius: 6px;
  transition: all 0.2s ease;
}
```

**聚焦状态**：
```css
.input:focus {
  outline: none;
  background: #FFFFFF;
  border-color: #0066FF;
  box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.1);
}
```

**错误状态**：
```css
.input.error {
  border-color: #FF4D4F;
  background: #FFF5F5;
}
.input.error:focus {
  border-color: #FF4D4F;
  box-shadow: 0 0 0 3px rgba(255, 77, 79, 0.1);
}
```

**成功状态**：
```css
.input.success {
  border-color: #00A854;
}
```

**辅助文字**：
- **字符计数**: 12px，颜色 #9CA3AF，在输入框右下角
- **错误提示**: 12px，颜色 #FF4D4F，在输入框下方
- **帮助文字**: 12px，颜色 #6B7280，在输入框下方

### 5. 多行输入框 (Textarea)

**样式**：与单行输入框一致
- **最小高度**: 80px
- **可调整**: 用户可拖拽调整高度
- **自动扩展**: (可选) 根据内容自动扩展

### 6. Markdown编辑器 (Markdown Editor)

**结构**：
```
┌─────────────────────────────────────────────────────────┐
│  [编辑区]                  [预览区]                     │
│  ┌────────────────────┐   ┌─────────────────────────┐  │
│  │ Markdown 编辑器     │   │ 实时预览               │  │
│  │                    │   │                         │  │
│  │                    │   │                         │  │
│  └────────────────────┘   └─────────────────────────┘  │
│                                                         │
│  [B] [I] [链接] [图片] [代码] [引用]                   │
└─────────────────────────────────────────────────────────┘
```

**布局**：Flexbox, 左右各50%
**最小高度**: 400px

**编辑器样式**：
```css
.markdown-editor {
  width: 100%;
  min-height: 400px;
  padding: 16px;
  font-family: var(--font-mono);
  font-size: 14px;
  line-height: 1.6;
  background: #FAFAFA;
  border: 1px solid #E5E7EB;
  border-radius: 6px;
  resize: vertical;
}
```

**预览区样式**：
```css
.markdown-preview {
  padding: 16px;
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 6px;
  overflow-y: auto;
}

/* Markdown 内容样式 */
.markdown-preview h1 { font-size: 24px; font-weight: 700; margin: 16px 0; }
.markdown-preview h2 { font-size: 20px; font-weight: 600; margin: 14px 0; }
.markdown-preview h3 { font-size: 18px; font-weight: 600; margin: 12px 0; }
.markdown-preview p { margin: 8px 0; line-height: 1.6; }
.markdown-preview ul, .markdown-preview ol { margin: 8px 0; padding-left: 24px; }
.markdown-preview code {
  padding: 2px 6px;
  background: #F3F4F6;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 13px;
}
.markdown-preview pre {
  padding: 12px;
  background: #1F2937;
  color: #F9FAFB;
  border-radius: 6px;
  overflow-x: auto;
}
.markdown-preview blockquote {
  padding-left: 12px;
  border-left: 3px solid #E5E7EB;
  color: #6B7280;
}
```

**工具栏样式**：
```css
.editor-toolbar {
  display: flex;
  gap: 8px;
  padding: 8px 0;
}

.toolbar-button {
  padding: 6px 12px;
  font-size: 13px;
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toolbar-button:hover {
  background: #F3F4F6;
  border-color: #D1D5DB;
}
```

### 7. 游戏类型选择 (Game Type Selector)

**结构**：
```
┌────────────────────────────────────────────┐
│  3.5 游戏类型                  必填 ✓    │
│                                            │
│  至少选择1个，最多5个                       │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ 🔍 搜索游戏类型...                   │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  热门:                                     │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐            │
│  │动作│ │冒险│ │休闲│ │解谜│            │
│  └────┘ └────┘ └────┘ └────┘            │
│                                            │
│  所有类型:                                 │
│  ☐ 动作  ☐ 冒险  ☐ 休闲  ☐ 解谜          │
│  ☐ 射击  ☐ 策略  ☐ 模拟  ☐ 角色扮演      │
│  ☐ 恐怖  ☐ 生存  ☐ 教育  ☐ 音乐          │
│  ☐ 视觉小说  ☐ 体育  ☐ 竞速               │
│                                            │
│  已选择 (2/5):                             │
│  [× 冒险] [× 解谜]                         │
│                                            │
│  预览: 您的游戏将被分类为"冒险、解谜"      │
└────────────────────────────────────────────┘
```

**搜索框样式**：
```css
.search-input {
  width: 100%;
  padding: 10px 12px 10px 40px;
  background: #FAFAFA url('search-icon.svg') no-repeat 12px center;
  border: 1px solid #E5E7EB;
  border-radius: 6px;
}
```

**类型选择项样式**：
```css
.type-option {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  margin: 4px;
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.type-option:hover {
  border-color: #0066FF;
  background: #E6F0FF;
}

.type-option.selected {
  background: #0066FF;
  border-color: #0066FF;
  color: #FFFFFF;
}
```

**已选标签样式**：
```css
.selected-tag {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  margin: 4px;
  background: #E6F0FF;
  border: 1px solid #0066FF;
  border-radius: 20px;
  color: #0066FF;
}

.remove-tag {
  margin-left: 8px;
  cursor: pointer;
  font-size: 16px;
}
```

### 8. 文件上传 (File Upload)

**封面图上传**：

**未上传状态**：
```
┌────────────────────────────────────────┐
│                                        │
│        📁 点击上传封面图                │
│                                        │
│      16:9 比例 | 推荐1920×1080         │
│      最小1280×720 | <2MB               │
│                                        │
│      支持 PNG、JPG、JPEG、WebP        │
│                                        │
└────────────────────────────────────────┘
```

**样式**：
```css
.file-upload-empty {
  width: 100%;
  aspect-ratio: 16/9;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #FAFAFA;
  border: 2px dashed #E5E7EB;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.file-upload-empty:hover {
  background: #F3F4F6;
  border-color: #0066FF;
}

.file-upload-icon {
  font-size: 48px;
  color: #9CA3AF;
  margin-bottom: 16px;
}

.file-upload-hint {
  font-size: 14px;
  color: #6B7280;
  text-align: center;
}

.file-upload-specs {
  font-size: 12px;
  color: #9CA3AF;
  margin-top: 8px;
}
```

**已上传状态**：
```
┌────────────────────────────────────────┐
│  [封面图预览]              [× 删除]    │
│                                        │
│  1920×1080 | 1.2 MB                    │
└────────────────────────────────────────┘
```

**样式**：
```css
.file-upload-filled {
  position: relative;
  width: 100%;
  aspect-ratio: 16/9;
  background: #F3F4F6;
  border: 2px solid #0066FF;
  border-radius: 8px;
  overflow: hidden;
}

.file-upload-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-upload-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px;
  background: rgba(0, 0, 0, 0.7);
  color: #FFFFFF;
  font-size: 12px;
}

.file-upload-remove {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 6px 12px;
  background: rgba(255, 77, 79, 0.9);
  color: #FFFFFF;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
```

**拖拽上传状态**：
```css
.file-upload-empty.dragging {
  background: #E6F0FF;
  border-color: #0066FF;
  border-style: solid;
}
```

### 9. 截图上传 (Screenshots Upload)

**结构**：
```
截图上传 (3-5张)              必填 ✓

┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│  +1 │ │  +2 │ │  +3 │ │  +4 │ │  +5 │
│     │ │     │ │     │ │     │ │     │
└─────┘ └─────┘ └─────┘ └─────┘ └─────┘

已上传: 0/5 张
```

**样式**：
```css
.screenshots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
}

.screenshot-slot {
  aspect-ratio: 16/9;
  background: #FAFAFA;
  border: 2px dashed #E5E7EB;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.screenshot-slot:hover {
  border-color: #0066FF;
  background: #F3F4F6;
}

.screenshot-slot.filled {
  border-style: solid;
  border-color: #0066FF;
  overflow: hidden;
}

.screenshot-number {
  font-size: 24px;
  font-weight: 600;
  color: #9CA3AF;
}
```

### 10. 复选框 (Checkbox)

**样式**：
```css
.checkbox-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox {
  width: 18px;
  height: 18px;
  margin-right: 8px;
  border: 2px solid #E5E7EB;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.checkbox.checked {
  background: #0066FF;
  border-color: #0066FF;
}

.checkbox.checked::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #FFFFFF;
  font-size: 12px;
  font-weight: 700;
}
```

### 11. 单选框 (Radio)

**样式**：
```css
.radio-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.radio {
  width: 18px;
  height: 18px;
  margin-right: 8px;
  border: 2px solid #E5E7EB;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.radio.checked {
  border-color: #0066FF;
}

.radio.checked::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 8px;
  height: 8px;
  background: #0066FF;
  border-radius: 50%;
}
```

### 12. 按钮 (Button)

**主要按钮 (Primary)**：
```css
.btn-primary {
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  color: #FFFFFF;
  background: #0066FF;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: #0052CC;
}

.btn-primary:active {
  background: #0047B3;
}

.btn-primary:disabled {
  background: #E5E7EB;
  color: #9CA3AF;
  cursor: not-allowed;
}
```

**次要按钮 (Secondary)**：
```css
.btn-secondary {
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  color: #1F2937;
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #F3F4F6;
  border-color: #D1D5DB;
}
```

**危险按钮 (Danger)**：
```css
.btn-danger {
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  color: #FFFFFF;
  background: #FF4D4F;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-danger:hover {
  background: #DC2626;
}
```

**按钮尺寸**：
- Small: padding 8px 16px, font-size 13px
- Base: padding 10px 20px, font-size 14px
- Large: padding 12px 24px, font-size 16px

---

## 交互设计

### 1. 滚动行为

**左侧导航锚点系统**：

```javascript
// 点击导航项平滑滚动
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', (e) => {
    e.preventDefault();
    const targetId = item.dataset.target;
    const targetElement = document.getElementById(targetId);

    targetElement.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    });
  });
});

// 滚动时自动高亮当前区域
const observerOptions = {
  root: null,
  rootMargin: '-20% 0px -70% 0px',
  threshold: 0
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const id = entry.target.id;
      document.querySelectorAll('.nav-item').forEach(nav => {
        nav.classList.remove('active');
        if (nav.dataset.target === id) {
          nav.classList.add('active');
        }
      });
    }
  });
}, observerOptions);

document.querySelectorAll('.form-section').forEach(section => {
  observer.observe(section);
});
```

### 2. 表单验证

**实时验证**：

```javascript
// 输入时实时验证
inputElement.addEventListener('input', (e) => {
  const value = e.target.value;
  const result = validateField(value);

  if (result.valid) {
    showSuccess(inputElement);
  } else {
    showError(inputElement, result.message);
  }

  updateCharacterCount(inputElement, value.length);
});

// 失焦时验证
inputElement.addEventListener('blur', (e) => {
  const value = e.target.value;
  const result = validateField(value);

  if (!result.valid) {
    showError(inputElement, result.message);
  }
});
```

**验证函数示例**：

```javascript
// 游戏标题验证
function validateGameTitle(title) {
  if (title.length === 0) {
    return { valid: false, message: '标题不能为空' };
  }
  if (title.length < 5) {
    return { valid: false, message: `标题至少需要5个字符，当前${title.length}个` };
  }
  if (title.length > 100) {
    return { valid: false, message: `标题超出${title.length - 100}个字符` };
  }
  return { valid: true };
}

// 游戏类型验证
function validateGameTypes(types) {
  if (types.length === 0) {
    return { valid: false, message: '请至少选择1个游戏类型' };
  }
  if (types.length > 5) {
    return { valid: false, message: '最多选择5个游戏类型' };
  }
  return { valid: true };
}
```

**显示/隐藏错误**：

```javascript
function showError(input, message) {
  input.classList.add('error');
  input.classList.remove('success');

  const errorElement = input.parentElement.querySelector('.error-message');
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.style.display = 'block';
  }
}

function showSuccess(input) {
  input.classList.remove('error');
  input.classList.add('success');

  const errorElement = input.parentElement.querySelector('.error-message');
  if (errorElement) {
    errorElement.style.display = 'none';
  }
}

function updateCharacterCount(input, count) {
  const counterElement = input.parentElement.querySelector('.char-count');
  if (counterElement) {
    const max = parseInt(input.dataset.maxLength);
    counterElement.textContent = `当前: ${count}/${max} 字符`;

    if (count > max) {
      counterElement.classList.add('error');
    } else {
      counterElement.classList.remove('error');
    }
  }
}
```

### 3. 文件上传

**拖拽上传**：

```javascript
const dropZone = document.querySelector('.file-upload-empty');

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('dragging');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('dragging');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('dragging');

  const files = e.dataTransfer.files;
  if (files.length > 0) {
    handleFileUpload(files[0]);
  }
});

// 点击上传
dropZone.addEventListener('click', () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/png,image/jpeg,image/webp';
  input.onchange = (e) => {
    if (e.target.files.length > 0) {
      handleFileUpload(e.target.files[0]);
    }
  };
  input.click();
});
```

**文件验证**：

```javascript
function handleFileUpload(file) {
  // 验证格式
  const validFormats = ['image/png', 'image/jpeg', 'image/webp'];
  if (!validFormats.includes(file.type)) {
    showError('不支持此格式，请上传 PNG、JPG、JPEG 或 WebP');
    return;
  }

  // 验证大小
  if (file.size > 2 * 1024 * 1024) {
    showError('文件大小不能超过 2MB');
    return;
  }

  // 验证尺寸
  const img = new Image();
  img.onload = () => {
    const ratio = img.width / img.height;
    if (Math.abs(ratio - 16/9) > 0.01) {
      showError('图片比例必须是 16:9');
      return;
    }

    if (img.width < 1280 || img.height < 720) {
      showWarning('建议使用 1920×1080，当前图片较小');
    }

    // 上传成功
    uploadSuccess(file, img);
  };
  img.src = URL.createObjectURL(file);
}
```

### 4. 自动保存

**自动保存逻辑**：

```javascript
let autoSaveTimer = null;
let lastSavedData = null;

// 防抖保存
function scheduleAutoSave() {
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer);
  }

  autoSaveTimer = setTimeout(() => {
    saveDraft();
  }, 30000); // 30秒后保存
}

// 收集表单数据
function collectFormData() {
  return {
    title: document.querySelector('#title').value,
    description: document.querySelector('#description').value,
    content: document.querySelector('#content').value,
    types: getSelectedGameTypes(),
    // ... 其他字段
  };
}

// 保存草稿
async function saveDraft() {
  const data = collectFormData();

  // 检查是否有变化
  if (JSON.stringify(data) === JSON.stringify(lastSavedData)) {
    return;
  }

  try {
    showSavingIndicator();

    const response = await fetch('/api/games/draft', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      lastSavedData = data;
      showSaveSuccess('上次自动保存: ' + new Date().toLocaleTimeString());
    } else {
      showSaveError('保存失败，请重试');
    }
  } catch (error) {
    showSaveError('网络错误，保存失败');
  }
}

// 监听所有输入变化
document.querySelectorAll('input, textarea, select').forEach(element => {
  element.addEventListener('input', scheduleAutoSave);
  element.addEventListener('change', scheduleAutoSave);
});
```

**保存状态指示**：

```javascript
function showSavingIndicator() {
  const indicator = document.querySelector('.save-status');
  indicator.textContent = '正在保存...';
  indicator.className = 'save-status saving';
}

function showSaveSuccess(message) {
  const indicator = document.querySelector('.save-status');
  indicator.textContent = message;
  indicator.className = 'save-status success';
  setTimeout(() => {
    indicator.className = 'save-status';
  }, 3000);
}

function showSaveError(message) {
  const indicator = document.querySelector('.save-status');
  indicator.textContent = message;
  indicator.className = 'save-status error';
}
```

### 5. 提交确认

**提交前验证**：

```javascript
async function handleSubmit() {
  // 验证所有必填项
  const validationResults = await validateAllFields();

  if (validationResults.hasErrors) {
    // 滚动到第一个错误项
    scrollToFirstError(validationResults.firstErrorField);
    return;
  }

  // 显示确认对话框
  const confirmed = await showSubmitConfirmation();
  if (!confirmed) {
    return;
  }

  // 提交
  try {
    showSubmitting();

    const data = collectFormData();
    const response = await fetch('/api/games/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      showSubmitSuccess();
      setTimeout(() => {
        window.location.href = '/games/my';
      }, 2000);
    } else {
      const error = await response.json();
      showSubmitError(error.message);
    }
  } catch (error) {
    showSubmitError('网络错误，请重试');
  }
}

function validateAllFields() {
  const results = {
    hasErrors: false,
    firstErrorField: null,
    errors: []
  };

  // 验证游戏标题
  const title = document.querySelector('#title');
  const titleResult = validateGameTitle(title.value);
  if (!titleResult.valid) {
    results.hasErrors = true;
    results.firstErrorField = results.firstErrorField || title;
    results.errors.push({ field: title, message: titleResult.message });
  }

  // 验证游戏类型
  const types = getSelectedGameTypes();
  const typesResult = validateGameTypes(types);
  if (!typesResult.valid) {
    results.hasErrors = true;
    results.errors.push({ field: null, message: typesResult.message });
  }

  // ... 其他验证

  return results;
}

function scrollToFirstError(firstErrorField) {
  if (firstErrorField) {
    firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
    firstErrorField.focus();
  }
}
```

---

## 响应式设计

### 断点系统

```css
:root {
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1440px;
}
```

### 平板适配 (768px - 1023px)

```css
@media (max-width: 1023px) {
  .page-layout {
    flex-direction: column;
  }

  .side-navigation {
    width: 100%;
    position: static;
    display: flex;
    overflow-x: auto;
    padding: 16px 0;
    border-bottom: 1px solid #E5E7EB;
  }

  .main-content {
    max-width: 100%;
  }
}
```

### 移动端适配 (<768px)

```css
@media (max-width: 767px) {
  /* 顶部栏 */
  .top-bar {
    height: 48px;
    padding: 0 16px;
  }

  .top-bar .title {
    font-size: 16px;
  }

  /* 导航折叠为顶部标签页 */
  .side-navigation {
    width: 100%;
    position: sticky;
    top: 48px;
    z-index: 10;
    background: #FFFFFF;
    display: flex;
    overflow-x: auto;
    padding: 12px 16px;
    border-bottom: 1px solid #E5E7EB;
    -webkit-overflow-scrolling: touch;
  }

  .nav-item {
    flex-shrink: 0;
    padding: 8px 16px;
    white-space: nowrap;
  }

  /* 主内容区 */
  .main-content {
    padding: 16px;
  }

  .form-card {
    padding: 16px;
    margin-bottom: 16px;
  }

  /* Markdown编辑器全屏 */
  .markdown-editor-container {
    flex-direction: column;
  }

  .markdown-editor,
  .markdown-preview {
    width: 100%;
    min-height: 200px;
  }

  /* 截图网格 */
  .screenshots-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  /* 按钮全宽 */
  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
```

---

## 代码实现

### HTML结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>游戏提交 - 惊蛰</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <!-- 顶部栏 -->
  <header class="top-bar">
    <button class="btn-back">← 返回</button>
    <h1 class="title">惊蛰 - 游戏提交</h1>
    <div class="actions">
      <button class="btn-secondary">保存草稿</button>
      <button class="btn-secondary">预览</button>
      <button class="btn-primary">提交</button>
    </div>
  </header>

  <!-- 主布局 -->
  <div class="page-layout">
    <!-- 左侧导航 -->
    <nav class="side-navigation">
      <div class="nav-item active" data-target="section-1">1. 标题 ✓</div>
      <div class="nav-item" data-target="section-2">2. 简介</div>
      <div class="nav-item" data-target="section-3">3. 正文</div>
      <div class="nav-item" data-target="section-4">4. 类型 ✓</div>
      <div class="nav-item" data-target="section-5">5. 媒体</div>
      <div class="nav-item" data-target="section-6">6. 链接</div>
      <div class="nav-item" data-target="section-7">7. 维度</div>
      <div class="nav-item" data-target="section-8">8. 确认</div>
    </nav>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 步骤1: 游戏标题 -->
      <section id="section-1" class="form-section">
        <div class="form-card">
          <div class="form-header">
            <h2>1. 游戏标题</h2>
            <span class="required-badge">必填</span>
          </div>

          <input
            type="text"
            id="title"
            class="input"
            placeholder="请输入游戏标题"
            data-min-length="5"
            data-max-length="100"
          >

          <div class="form-hint">
            <span class="char-count">当前: 0/100 字符</span>
            <span class="error-message" style="display: none;"></span>
          </div>
        </div>
      </section>

      <!-- 步骤2: 游戏简介 -->
      <section id="section-2" class="form-section">
        <div class="form-card">
          <div class="form-header">
            <h2>2. 游戏简介</h2>
            <span class="optional-badge">可选</span>
          </div>

          <textarea
            id="description"
            class="textarea"
            placeholder="简要描述你的游戏（最多100字符）"
            data-max-length="100"
          ></textarea>

          <div class="form-hint">
            <span class="char-count">当前: 0/100 字符</span>
          </div>
        </div>
      </section>

      <!-- 步骤3: 游戏正文 -->
      <section id="section-3" class="form-section">
        <div class="form-card">
          <div class="form-header">
            <h2>3. 游戏正文</h2>
            <span class="required-badge">必填</span>
          </div>

          <div class="markdown-editor-container">
            <div class="markdown-editor-wrapper">
              <div class="editor-toolbar">
                <button class="toolbar-button" data-action="bold">B</button>
                <button class="toolbar-button" data-action="italic">I</button>
                <button class="toolbar-button" data-action="link">链接</button>
                <button class="toolbar-button" data-action="image">图片</button>
                <button class="toolbar-button" data-action="code">代码</button>
                <button class="toolbar-button" data-action="quote">引用</button>
              </div>
              <textarea
                id="content"
                class="markdown-editor"
                placeholder="使用Markdown语法编写游戏介绍..."
              ></textarea>
            </div>

            <div id="preview" class="markdown-preview">
              <!-- 实时预览内容 -->
            </div>
          </div>

          <div class="form-hint">
            <span class="char-count">当前: 0 字符（至少200字符）</span>
          </div>
        </div>
      </section>

      <!-- 步骤3.5: 游戏类型 -->
      <section id="section-4" class="form-section">
        <div class="form-card">
          <div class="form-header">
            <h2>3.5 游戏类型</h2>
            <span class="required-badge">必填</span>
          </div>

          <p class="form-description">至少选择1个，最多5个</p>

          <input
            type="text"
            id="game-type-search"
            class="input search-input"
            placeholder="搜索游戏类型..."
          >

          <div class="game-type-section">
            <h3>热门</h3>
            <div class="type-options">
              <button class="type-option" data-value="action">动作</button>
              <button class="type-option" data-value="adventure">冒险</button>
              <button class="type-option" data-value="casual">休闲</button>
              <button class="type-option" data-value="puzzle">解谜</button>
            </div>
          </div>

          <div class="game-type-section">
            <h3>所有类型</h3>
            <div class="type-grid">
              <label class="checkbox-wrapper">
                <input type="checkbox" value="action"> 动作
              </label>
              <label class="checkbox-wrapper">
                <input type="checkbox" value="adventure"> 冒险
              </label>
              <!-- 更多类型... -->
            </div>
          </div>

          <div class="selected-types">
            <h4>已选择 (0/5):</h4>
            <div id="selected-tags" class="selected-tags">
              <span class="empty-hint">暂无选择</span>
            </div>
          </div>

          <div class="type-preview">
            预览: 您的游戏将被分类为"<span id="type-preview-text">-</span>"
          </div>
        </div>
      </section>

      <!-- 更多步骤... -->

    </main>
  </div>

  <!-- 保存状态 -->
  <div class="save-status"></div>

  <script src="app.js"></script>
</body>
</html>
```

### CSS样式

```css
/* 导入设计系统变量 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-body);
  font-size: var(--font-size-base);
  line-height: var(--line-height-normal);
  color: var(--color-text-primary);
  background: var(--color-bg-page);
}

/* 页面布局 */
.page-layout {
  display: flex;
  max-width: var(--breakpoint-2xl);
  margin: 0 auto;
  padding: var(--spacing-8);
}

/* 顶部栏 */
.top-bar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 var(--spacing-8);
  background: var(--color-bg-page);
  border-bottom: 1px solid var(--color-border-default);
}

/* 主内容区 */
.main-content {
  flex: 1;
  max-width: 900px;
}

/* 表单区域 */
.form-section {
  margin-bottom: var(--spacing-6);
}

.form-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  padding: var(--spacing-6);
  border: 1px solid var(--color-border-default);
}

.form-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-4);
}

.form-header h2 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.required-badge {
  padding: 2px 8px;
  font-size: var(--font-size-xs);
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-radius: var(--radius-base);
}

.optional-badge {
  padding: 2px 8px;
  font-size: var(--font-size-xs);
  background: var(--color-gray-200);
  color: var(--color-text-tertiary);
  border-radius: var(--radius-base);
}

.form-hint {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-2);
}

.char-count {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.error-message {
  font-size: var(--font-size-xs);
  color: var(--color-text-error);
}

/* 保存状态 */
.save-status {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 12px 20px;
  background: var(--color-gray-900);
  color: var(--color-gray-50);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.save-status.show {
  opacity: 1;
}

.save-status.success {
  background: var(--color-success);
}

.save-status.error {
  background: var(--color-error);
}
```

### JavaScript逻辑

```javascript
// 应用状态
const state = {
  formData: {
    title: '',
    description: '',
    content: '',
    gameTypes: [],
    // ... 其他字段
  },
  validationResults: {},
  autoSaveTimer: null,
  lastSavedData: null
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
  initializeNavigation();
  initializeFormValidation();
  initializeAutoSave();
  initializeMarkdownEditor();
  initializeGameTypes();
  initializeFileUpload();
});

// 导航系统
function initializeNavigation() {
  // 点击导航项平滑滚动
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
      const targetId = item.dataset.target;
      const targetElement = document.getElementById(targetId);

      targetElement.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    });
  });

  // 滚动时自动高亮当前区域
  const observerOptions = {
    root: null,
    rootMargin: '-20% 0px -70% 0px',
    threshold: 0
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        updateActiveNavigation(id);
      }
    });
  }, observerOptions);

  document.querySelectorAll('.form-section').forEach(section => {
    observer.observe(section);
  });
}

function updateActiveNavigation(activeId) {
  document.querySelectorAll('.nav-item').forEach(nav => {
    nav.classList.remove('active');
    if (nav.dataset.target === activeId) {
      nav.classList.add('active');
    }
  });
}

// 表单验证
function initializeFormValidation() {
  // 游戏标题
  const titleInput = document.getElementById('title');
  titleInput.addEventListener('input', (e) => {
    const value = e.target.value;
    state.formData.title = value;

    const result = validateGameTitle(value);
    handleValidationResult(titleInput, result);
    updateCharacterCount(titleInput, value.length, 5, 100);
  });

  // 更多字段验证...
}

function validateGameTitle(title) {
  if (title.length === 0) {
    return { valid: false, message: '标题不能为空' };
  }
  if (title.length < 5) {
    return { valid: false, message: `标题至少需要5个字符，当前${title.length}个` };
  }
  if (title.length > 100) {
    return { valid: false, message: `标题超出${title.length - 100}个字符` };
  }
  return { valid: true };
}

function handleValidationResult(input, result) {
  if (result.valid) {
    showSuccess(input);
  } else {
    showError(input, result.message);
  }
}

function showSuccess(input) {
  input.classList.remove('error');
  input.classList.add('success');

  const errorElement = input.parentElement.querySelector('.error-message');
  if (errorElement) {
    errorElement.style.display = 'none';
  }
}

function showError(input, message) {
  input.classList.add('error');
  input.classList.remove('success');

  const errorElement = input.parentElement.querySelector('.error-message');
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.style.display = 'block';
  }
}

function updateCharacterCount(input, count, min, max) {
  const counterElement = input.parentElement.querySelector('.char-count');
  if (counterElement) {
    let text = `当前: ${count}/${max} 字符`;
    if (count < min) {
      text += ` (还需${min - count}个字符)`;
    }
    counterElement.textContent = text;
  }
}

// 自动保存
function initializeAutoSave() {
  document.querySelectorAll('input, textarea, select').forEach(element => {
    element.addEventListener('input', scheduleAutoSave);
    element.addEventListener('change', scheduleAutoSave);
  });
}

function scheduleAutoSave() {
  if (state.autoSaveTimer) {
    clearTimeout(state.autoSaveTimer);
  }

  state.autoSaveTimer = setTimeout(() => {
    saveDraft();
  }, 30000);
}

async function saveDraft() {
  const data = collectFormData();

  if (JSON.stringify(data) === JSON.stringify(state.lastSavedData)) {
    return;
  }

  try {
    showSavingIndicator();

    const response = await fetch('/api/games/draft', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      state.lastSavedData = data;
      showSaveSuccess('上次自动保存: ' + new Date().toLocaleTimeString());
    } else {
      showSaveError('保存失败，请重试');
    }
  } catch (error) {
    showSaveError('网络错误，保存失败');
  }
}

function collectFormData() {
  return {
    title: document.getElementById('title').value,
    description: document.getElementById('description').value,
    content: document.getElementById('content').value,
    gameTypes: Array.from(document.querySelectorAll('.type-option.selected'))
      .map(btn => btn.dataset.value),
    // ... 其他字段
  };
}

function showSavingIndicator() {
  const indicator = document.querySelector('.save-status');
  indicator.textContent = '正在保存...';
  indicator.className = 'save-status show';
}

function showSaveSuccess(message) {
  const indicator = document.querySelector('.save-status');
  indicator.textContent = message;
  indicator.className = 'save-status show success';
  setTimeout(() => {
    indicator.className = 'save-status';
  }, 3000);
}

function showSaveError(message) {
  const indicator = document.querySelector('.save-status');
  indicator.textContent = message;
  indicator.className = 'save-status show error';
}

// Markdown编辑器
function initializeMarkdownEditor() {
  const editor = document.getElementById('content');
  const preview = document.getElementById('preview');

  editor.addEventListener('input', (e) => {
    const markdown = e.target.value;
    const html = parseMarkdown(markdown);
    preview.innerHTML = html;

    state.formData.content = markdown;
    scheduleAutoSave();
  });

  // 工具栏按钮
  document.querySelectorAll('.toolbar-button').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const action = e.target.dataset.action;
      insertMarkdownSyntax(action);
    });
  });
}

function parseMarkdown(markdown) {
  // 简化的Markdown解析
  // 实际项目中应该使用成熟的库（如marked.js）
  return markdown
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*)\*/gim, '<em>$1</em>')
    .replace(/\n/gim, '<br>');
}

function insertMarkdownSyntax(action) {
  const editor = document.getElementById('content');
  const start = editor.selectionStart;
  const end = editor.selectionEnd;
  const text = editor.value;
  const selectedText = text.substring(start, end);

  let syntax = '';
  switch (action) {
    case 'bold':
      syntax = `**${selectedText || '粗体文本'}**`;
      break;
    case 'italic':
      syntax = `*${selectedText || '斜体文本'}*`;
      break;
    case 'link':
      syntax = `[${selectedText || '链接文本'}](url)`;
      break;
    case 'image':
      syntax = `![${selectedText || '图片描述'}](url)`;
      break;
    case 'code':
      syntax = `\`${selectedText || '代码'}\``;
      break;
    case 'quote':
      syntax = `> ${selectedText || '引用内容'}`;
      break;
  }

  editor.value = text.substring(0, start) + syntax + text.substring(end);
  editor.focus();
}

// 游戏类型选择
function initializeGameTypes() {
  const searchInput = document.getElementById('game-type-search');
  const typeOptions = document.querySelectorAll('.type-option');

  // 搜索过滤
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    typeOptions.forEach(option => {
      const value = option.dataset.value.toLowerCase();
      option.style.display = value.includes(query) ? 'inline-flex' : 'none';
    });
  });

  // 类型选择
  typeOptions.forEach(option => {
    option.addEventListener('click', () => {
      const value = option.dataset.value;
      toggleGameType(value, option);
    });
  });
}

function toggleGameType(value, element) {
  const index = state.formData.gameTypes.indexOf(value);

  if (index > -1) {
    // 取消选择
    state.formData.gameTypes.splice(index, 1);
    element.classList.remove('selected');
  } else {
    // 选择
    if (state.formData.gameTypes.length >= 5) {
      showError('最多选择5个游戏类型');
      return;
    }
    state.formData.gameTypes.push(value);
    element.classList.add('selected');
  }

  updateSelectedTypes();
  scheduleAutoSave();
}

function updateSelectedTypes() {
  const container = document.getElementById('selected-tags');
  const types = state.formData.gameTypes;
  const typeNames = {
    action: '动作',
    adventure: '冒险',
    casual: '休闲',
    puzzle: '解谜',
    // ... 其他类型映射
  };

  if (types.length === 0) {
    container.innerHTML = '<span class="empty-hint">暂无选择</span>';
  } else {
    container.innerHTML = types.map(type =>
      `<span class="selected-tag">
        ${typeNames[type]}
        <span class="remove-tag" data-type="${type}">×</span>
      </span>`
    ).join('');

    // 绑定删除事件
    container.querySelectorAll('.remove-tag').forEach(btn => {
      btn.addEventListener('click', () => {
        const type = btn.dataset.type;
        removeGameType(type);
      });
    });
  }

  // 更新计数
  document.querySelector('.selected-types h4').textContent =
    `已选择 (${types.length}/5):`;

  // 更新预览
  const previewText = types.length > 0
    ? types.map(t => typeNames[t]).join('、')
    : '-';
  document.getElementById('type-preview-text').textContent = previewText;
}

function removeGameType(value) {
  const index = state.formData.gameTypes.indexOf(value);
  if (index > -1) {
    state.formData.gameTypes.splice(index, 1);

    const option = document.querySelector(`.type-option[data-value="${value}"]`);
    if (option) {
      option.classList.remove('selected');
    }

    updateSelectedTypes();
    scheduleAutoSave();
  }
}

// 文件上传
function initializeFileUpload() {
  const dropZone = document.querySelector('.file-upload-empty');

  if (!dropZone) return;

  // 拖拽上传
  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragging');
  });

  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragging');
  });

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragging');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0], dropZone);
    }
  });

  // 点击上传
  dropZone.addEventListener('click', () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/png,image/jpeg,image/webp';
    input.onchange = (e) => {
      if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0], dropZone);
      }
    };
    input.click();
  });
}

function handleFileUpload(file, container) {
  // 验证格式
  const validFormats = ['image/png', 'image/jpeg', 'image/webp'];
  if (!validFormats.includes(file.type)) {
    showError('不支持此格式，请上传 PNG、JPG、JPEG 或 WebP');
    return;
  }

  // 验证大小
  if (file.size > 2 * 1024 * 1024) {
    showError('文件大小不能超过 2MB');
    return;
  }

  // 验证尺寸
  const img = new Image();
  img.onload = () => {
    const ratio = img.width / img.height;
    if (Math.abs(ratio - 16/9) > 0.01) {
      showError('图片比例必须是 16:9');
      return;
    }

    if (img.width < 1280 || img.height < 720) {
      showWarning('建议使用 1920×1080，当前图片较小');
    }

    // 显示预览
    displayPreview(file, img, container);
  };
  img.src = URL.createObjectURL(file);
}

function displayPreview(file, img, container) {
  container.className = 'file-upload-filled';
  container.innerHTML = `
    <img src="${img.src}" class="file-upload-preview" alt="封面图">
    <div class="file-upload-info">
      ${img.width}×${img.height} | ${formatFileSize(file.size)}
    </div>
    <button class="file-upload-remove" onclick="removeFileUpload(this)">×</button>
  `;
}

function removeFileUpload(button) {
  const container = button.closest('.file-upload-filled');
  container.className = 'file-upload-empty';
  container.innerHTML = `
    <div class="file-upload-icon">📁</div>
    <div class="file-upload-hint">点击上传封面图</div>
    <div class="file-upload-specs">
      16:9 比例 | 推荐1920×1080<br>
      最小1280×720 | <2MB<br>
      支持 PNG、JPG、JPEG、WebP
    </div>
  `;
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
```

---

## 可访问性

### ARIA标签

```html
<!-- 表单字段 -->
<label for="title" class="form-label">
  游戏标题
  <span class="required-badge" aria-label="必填">必填</span>
</label>
<input
  type="text"
  id="title"
  class="input"
  required
  aria-describedby="title-hint title-error"
  aria-invalid="false"
>
<span id="title-hint" class="char-count">当前: 0/100 字符</span>
<span id="title-error" class="error-message" role="alert" aria-live="polite"></span>

<!-- 导航 -->
<nav class="side-navigation" aria-label="表单步骤导航">
  <a href="#section-1" class="nav-item" aria-current="step">1. 标题</a>
  <a href="#section-2" class="nav-item">2. 简介</a>
  <!-- ... -->
</nav>
```

### 键盘导航

```javascript
// Tab键顺序自然
// 焦点样式清晰
input:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

// 快捷键
document.addEventListener('keydown', (e) => {
  // Ctrl/Cmd + S 保存草稿
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault();
    saveDraft();
  }

  // Ctrl/Cmd + Enter 提交
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    handleSubmit();
  }
});
```

### 屏幕阅读器支持

```javascript
// 动态更新时的通知
function announceToScreenReader(message) {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', 'polite');
  announcement.className = 'sr-only';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}

// 使用示例
announceToScreenReader('草稿已保存');
```

---

## 验收标准

### 功能完整性
- [ ] 7步表单全部实现
- [ ] 实时验证正常工作
- [ ] 自动保存每30秒触发
- [ ] Markdown编辑器实时预览
- [ ] 文件上传支持拖拽
- [ ] 游戏类型选择限制1-5个
- [ ] 提交前验证所有必填项

### 视觉质量
- [ ] 符合"精准实用主义"设计方向
- [ ] 无Inter、Roboto等通用字体
- [ ] 无紫色渐变等AI设计陈词滥调
- [ ] 所有交互有即时视觉反馈
- [ ] 错误状态清晰明确
- [ ] 空状态友好引导

### 性能优化
- [ ] 首屏加载 < 2秒
- [ ] 交互响应 < 100ms
- [ ] 自动保存防抖处理
- [ ] 图片懒加载
- [ ] 无内存泄漏

### 浏览器兼容性
- [ ] Chrome/Edge (最新版)
- [ ] Firefox (最新版)
- [ ] Safari (最新版)
- [ ] 移动端 Safari/Chrome

### 可访问性
- [ ] 所有交互元素可键盘访问
- [ ] ARIA标签完整
- [ ] 焦点管理正确
- [ ] 屏幕阅读器友好
- [ ] 色彩对比度符合WCAG AA标准

---

**文档版本**: v1.0
**最后更新**: 2025-01-12
**设计师**: Claude (frontend-ui-ux skill)
**状态**: ✅ 完成，可用于开发和设计
