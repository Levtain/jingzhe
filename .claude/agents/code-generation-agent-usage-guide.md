# code-generation-agent 使用指南

> **Agent名称**: code-generation-agent
> **版本**: v1.0
> **创建时间**: 2025-01-11
> **用途**: 从设计文档自动生成代码框架和项目结构

---

## 🎯 核心功能

code-generation-agent 是一个专门用于代码生成的Agent,能从设计文档自动生成完整的项目结构、样板代码和测试框架。

### 主要能力

- 📁 **自动生成目录结构**: 前后端完整项目结构
- ⚙️ **生成配置文件**: package.json, .env, ESLint等
- 💻 **生成样板代码**: Model, Service, Controller, 组件
- 🧪 **生成测试框架**: Jest测试样板
- 📝 **生成TODO清单**: 实现任务列表

---

## 🚀 快速开始

### 基本用法

**方式1: 从设计文档生成**
```
"生成代码"
"generate code"
"开始开发"
```

**方式2: 创建项目结构**
```
"创建游戏提交系统的项目结构"
"generate project structure for payment system"
```

**方式3: 初始化新模块**
```
"开始开发评分系统"
"initialize ranking module"
```

### 使用场景

```yaml
设计完成后:
  → 设计文档审核通过
  → "生成代码"
  → Agent生成完整框架
  → 开始填充业务逻辑

新功能开发:
  → 完成功能设计
  → "创建项目结构"
  → Agent生成样板代码
  → 快速启动开发

项目初始化:
  → 从零开始项目
  → "生成项目框架"
  → Agent生成完整结构
  → 预置最佳实践
```

---

## 📋 支持的技术栈

### 初期支持 (v1.0)

**前端**:
- React
- Vue.js
- Angular

**后端**:
- Node.js (Express)
- Python (Flask, Django)
- Java (Spring Boot)

**数据库**:
- MongoDB
- PostgreSQL
- MySQL

### 技术栈自动识别

Agent会从设计文档中自动识别:
- 前端框架 (React/Vue/Angular)
- 后端框架 (Node.js/Python/Java)
- 数据库 (MongoDB/PostgreSQL/MySQL)

**示例**:
```markdown
设计文档提到:
- "使用React构建前端"
- "后端采用Node.js"
- "数据库使用MongoDB"

Agent自动识别:
→ 技术栈 = {frontend: React, backend: Node.js, database: MongoDB}
```

---

## 📁 生成的项目结构

### React + Node.js + MongoDB 全栈示例

```
project-root/
├── backend/
│   ├── src/
│   │   ├── controllers/
│   │   │   └── {Module}Controller.js
│   │   ├── models/
│   │   │   └── {Module}Model.js
│   │   ├── routes/
│   │   │   └── {Module}Routes.js
│   │   ├── services/
│   │   │   └── {Module}Service.js
│   │   ├── middleware/
│   │   │   ├── auth.js
│   │   │   └── validation.js
│   │   ├── utils/
│   │   │   ├── logger.js
│   │   │   └── response.js
│   │   ├── config/
│   │   │   └── database.js
│   │   └── app.js
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── controllers/
│   │   │   └── services/
│   │   └── integration/
│   ├── .env.example
│   ├── package.json
│   └── .eslintrc.js
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── {module}/
│   │   │       ├── {Module}List.jsx
│   │   │       └── {Module}Form.jsx
│   │   ├── pages/
│   │   │   └── {Module}Page.jsx
│   │   ├── services/
│   │   │   └── {Module}Service.js
│   │   ├── hooks/
│   │   │   └── use{Module}.js
│   │   ├── styles/
│   │   │   └── {Module}.module.css
│   │   └── index.js
│   ├── package.json
│   └── .env.example
│
└── README.md
```

---

## 💻 生成的代码详解

### 后端代码 (Node.js)

**1. Model (Mongoose)**:
```javascript
const mongoose = require('mongoose');
const { Schema } = mongoose;

const ModuleSchema = new Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  description: String,
  status: {
    type: String,
    enum: ['active', 'inactive', 'deleted'],
    default: 'active'
  }
}, {
  timestamps: true
});

// Indexes
ModuleSchema.index({ name: 1 });

// Methods
ModuleSchema.methods.isActive = function() {
  return this.status === 'active';
};

module.exports = mongoose.model('Module', ModuleSchema);
```

**2. Service Layer**:
```javascript
const Module = require('../models/ModuleModel');
const APIError = require('../utils/APIError');

class ModuleService {
  static async findAll(options = {}) {
    const { page, limit, sort } = options;
    const query = Module.find({});

    if (page && limit) {
      query.skip((page - 1) * limit).limit(limit);
    }

    const data = await query;
    const total = await Module.countDocuments();

    return { data, pagination: { total, page, limit } };
  }

  static async findById(id) {
    const module = await Module.findById(id);
    if (!module) {
      throw new APIError('Module not found', 404);
    }
    return module;
  }

  static async create(data) {
    return await Module.create(data);
  }

  static async update(id, data) {
    const module = await Module.findByIdAndUpdate(
      id,
      data,
      { new: true, runValidators: true }
    );
    if (!module) {
      throw new APIError('Module not found', 404);
    }
    return module;
  }

  static async delete(id) {
    const module = await Module.findByIdAndDelete(id);
    if (!module) {
      throw new APIError('Module not found', 404);
    }
    return module;
  }
}

module.exports = ModuleService;
```

**3. Controller**:
```javascript
const ModuleService = require('../services/ModuleService');
const { catchAsync } = require('../utils/catchAsync');
const { response } = require('../utils/response');

exports.getAllModules = catchAsync(async (req, res) => {
  const { page = 1, limit = 10 } = req.query;
  const result = await ModuleService.findAll({ page, limit });
  response.success(res, result);
});

exports.getModuleById = catchAsync(async (req, res) => {
  const module = await ModuleService.findById(req.params.id);
  response.success(res, { data: module });
});

exports.createModule = catchAsync(async (req, res) => {
  const module = await ModuleService.create(req.body);
  response.created(res, {
    data: module,
    message: 'Module created successfully'
  });
});

exports.updateModule = catchAsync(async (req, res) => {
  const module = await ModuleService.update(req.params.id, req.body);
  response.success(res, {
    data: module,
    message: 'Module updated successfully'
  });
});

exports.deleteModule = catchAsync(async (req, res) => {
  await ModuleService.delete(req.params.id);
  response.success(res, {
    message: 'Module deleted successfully'
  });
});
```

### 前端代码 (React)

**1. Service**:
```javascript
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000/api';

const moduleService = {
  findAll: async (params = {}) => {
    const response = await axios.get(`${API_URL}/modules`, { params });
    return response.data;
  },

  findById: async (id) => {
    const response = await axios.get(`${API_URL}/modules/${id}`);
    return response.data;
  },

  create: async (data) => {
    const response = await axios.post(`${API_URL}/modules`, data);
    return response.data;
  },

  update: async (id, data) => {
    const response = await axios.put(`${API_URL}/modules/${id}`, data);
    return response.data;
  },

  delete: async (id) => {
    const response = await axios.delete(`${API_URL}/modules/${id}`);
    return response.data;
  }
};

export default moduleService;
```

**2. Component**:
```jsx
import React, { useState, useEffect } from 'react';
import moduleService from '../services/moduleService';
import './ModuleList.module.css';

const ModuleList = () => {
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchModules();
  }, []);

  const fetchModules = async () => {
    setLoading(true);
    try {
      const response = await moduleService.findAll();
      setModules(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure?')) return;

    try {
      await moduleService.delete(id);
      setModules(modules.filter(m => m._id !== id));
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="module-list">
      <h1>Modules</h1>

      <button onClick={() => {/* Navigate to create */}}>
        Create Module
      </button>

      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {modules.map(module => (
            <tr key={module._id}>
              <td>{module.name}</td>
              <td>{module.description}</td>
              <td>{module.status}</td>
              <td>
                <button>Edit</button>
                <button onClick={() => handleDelete(module._id)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ModuleList;
```

### 测试代码

**Jest Test**:
```javascript
const ModuleService = require('../../src/services/ModuleService');
const Module = require('../../src/models/ModuleModel');

describe('ModuleService', () => {
  describe('findAll', () => {
    it('should return paginated results', async () => {
      const mockData = [
        { name: 'Test 1' },
        { name: 'Test 2' }
      ];

      jest.spyOn(Module, 'find').mockReturnValue({
        skip: jest.fn().mockReturnThis(),
        limit: jest.fn().mockReturnThis(),
        sort: jest.fn().mockResolvedValue(mockData)
      });

      jest.spyOn(Module, 'countDocuments').mockResolvedValue(2);

      const result = await ModuleService.findAll({ page: 1, limit: 10 });

      expect(result.data).toEqual(mockData);
      expect(result.pagination.total).toBe(2);
    });
  });

  describe('findById', () => {
    it('should return module by id', async () => {
      const mockModule = { _id: '123', name: 'Test' };

      jest.spyOn(Module, 'findById').mockResolvedValue(mockModule);

      const result = await ModuleService.findById('123');

      expect(result).toEqual(mockModule);
    });

    it('should throw error if not found', async () => {
      jest.spyOn(Module, 'findById').mockResolvedValue(null);

      await expect(ModuleService.findById('123'))
        .rejects
        .toThrow('Module not found');
    });
  });
});
```

---

## 📝 实现TODO清单

Agent会生成详细的实现任务清单:

```markdown
## 📝 Implementation TODO List

### 🔴 Must Complete (Core Features)

- [ ] Implement custom Service methods
  - File: src/services/{Module}Service.js
  - Estimated: 2 hours

- [ ] Implement custom Controller endpoints
  - File: src/controllers/{Module}Controller.js
  - Estimated: 2 hours

- [ ] Implement validation rules
  - File: src/middleware/validation.js
  - Estimated: 1 hour

- [ ] Implement frontend components business logic
  - File: src/components/{module}/*
  - Estimated: 4 hours

### 🟡 Should Complete (Enhancements)

- [ ] Add caching layer
  - File: src/services/cacheService.js
  - Estimated: 1 hour

- [ ] Implement search functionality
  - Estimated: 1 hour

- [ ] Add export functionality
  - Estimated: 1 hour

### 🟢 Nice to Have (Optimizations)

- [ ] Add more unit tests
  - Estimated: 2 hours

- [ ] Add integration tests
  - Estimated: 2 hours

- [ ] Performance optimization
  - Estimated: 1 hour

**Total Estimated Time**: 17-21 hours
```

---

## 💡 使用技巧

### 技巧1: 准备设计文档

```yaml
设计文档应包含:
  1. 模块名称和描述
  2. 技术栈选择
  3. 数据模型定义
  4. API端点列表
  5. 主要功能需求

Agent会自动:
  - 识别技术栈
  - 提取数据模型
  - 生成对应的代码结构
```

### 技巧2: 自定义技术栈

```yaml
在设计文档中明确说明:
  "前端使用Vue.js"
  "后端使用Python Flask"
  "数据库使用PostgreSQL"

Agent会根据说明:
  - 生成Vue.js组件
  - 生成Python Flask代码
  - 配置PostgreSQL连接
```

### 技巧3: 增量生成

```yaml
第一次生成:
  "生成评分系统代码"
  → 生成完整框架

后续补充:
  "添加导出功能"
  → 只生成导出相关代码

避免:
  - 覆盖已有文件
  - 保留手动修改
```

### 技巧4: 团队协作

```yaml
统一代码风格:
  - 整个团队使用同一个Agent生成
  - 保证代码风格一致
  - 减少Code Review负担

快速原型:
  - 快速生成原型
  - 验证设计可行性
  - 早期发现问题
```

---

## ⚠️ 注意事项

### 何时使用

```yaml
✅ 推荐使用:
  - 设计文档完成后
  - 新模块开发开始
  - 项目初始化
  - 快速原型开发

❌ 不推荐使用:
  - 项目已经存在(会覆盖)
  - 只需要简单代码(手动更快)
  - 技术栈不支持
```

### 代码质量

```yaml
生成的代码:
  - 是样板代码
  - 遵循最佳实践
  - 需要添加业务逻辑
  - 需要测试和优化

你必须:
  - 审查生成的代码
  - 添加具体业务逻辑
  - 编写完整的测试
  - 优化性能
```

### 版本控制

```yaml
建议:
  - 生成代码前提交当前代码
  - 生成后立即提交
  - 使用Git分支开发
  - Code Review后再合并

避免:
  - 直接在主分支生成
  - 覆盖已有代码
```

---

## 🔄 与其他Agent的配合

### 完整开发流程

```yaml
1. design-audit-agent
   → 审核设计质量

2. 设计审核通过
   → 准备开始开发

3. code-generation-agent ← 本Agent
   → 生成代码框架

4. 开发者填充业务逻辑
   → 实现具体功能

5. code-review-agent
   → 审核代码质量

6. completion-check-agent
   → 验证完成度
```

### Agent协作

```yaml
workflow-orchestrator-agent:
  "开始新模块开发"
  → 调用 code-generation-agent
  → 生成代码框架
  → 提供实现TODO

其他Agent:
  - design-audit-agent: 设计完成后触发
  - code-review-agent: 代码完成后触发
  - completion-check-agent: 验证完成度
```

---

## 📞 常见问题

### Q1: 生成的代码可以直接用吗?

**A**: 不完全是。生成的代码:
- ✅ 可以运行(结构完整)
- ❌ 没有业务逻辑
- ❌ 需要你填充具体实现
- ❌ 需要添加完整测试

**建议**: 作为起点,然后添加你的业务逻辑

### Q2: 会覆盖已有文件吗?

**A**: 会。所以建议:
1. 在新目录生成
2. 或使用Git分支
3. 或备份现有代码

**未来版本**: 会支持增量生成,避免覆盖

### Q3: 支持我的技术栈吗?

**A**:
- **v1.0**: React/Vue/Angular + Node.js/Python/Java + Mongo/PostgreSQL/MySQL
- **v1.1+**: 会支持更多技术栈

**如果不支持**: Agent会使用默认技术栈生成

### Q4: 如何自定义生成模板?

**A**:
- **v1.0**: 不支持自定义
- **未来版本**: 会支持配置文件自定义模板

**当前**: 生成后手动修改

### Q5: 生成的代码质量如何?

**A**:
- ✅ 遵循最佳实践
- ✅ 统一代码风格
- ✅ 包含基础功能
- ⚠️ 需要添加业务逻辑
- ⚠️ 需要性能优化

**建议**: 作为起点,然后根据需求优化

---

## 🎓 最佳实践

### 实践1: 设计驱动

```yaml
1. 完成详细设计
   → 明确技术栈
   → 定义数据模型
   → 列出API端点

2. 审核设计
   → design-audit-agent审核
   → 确保设计质量

3. 生成代码
   → code-generation-agent生成
   → 获得完整框架

4. 填充逻辑
   → 按TODO清单实现
   → 快速完成开发
```

### 实践2: 快速原型

```yaml
1. 快速设计核心功能
2. 生成代码框架
3. 填充基本逻辑
4. 验证可行性
5. 迭代优化
```

### 实践3: 团队统一

```yaml
1. 团队统一技术栈
2. 统一代码生成配置
3. 所有人使用相同Agent生成
4. 保证代码风格一致
5. 减少协作成本
```

---

## 📈 效果对比

### 使用前

```yaml
问题1: 创建结构繁琐
  - 手动创建目录
  - 手动创建文件
  - 容易遗漏文件

问题2: 样板代码重复
  - 每次都写相似代码
  - 浪费时间
  - 容易出错

问题3: 风格不统一
  - 不同开发者风格不同
  - 增加Code Review负担
```

### 使用后

```yaml
解决1: 一键生成
  - 自动创建完整结构
  - 不会遗漏文件
  - 节省90%时间

解决2: 避免重复
  - 样板代码自动生成
  - 专注业务逻辑
  - 减少错误

解决3: 统一风格
  - 整个团队风格一致
  - 减少Review成本
  - 提升代码质量
```

---

## 🔄 版本历史

### v1.0 (2025-01-11)

**新增**:
- 支持React/Vue/Angular前端
- 支持Node.js/Python/Java后端
- 支持MongoDB/PostgreSQL/MySQL
- 自动识别技术栈
- 生成完整项目结构
- 生成样板代码
- 生成测试框架

**特点**:
- 遵循最佳实践
- 统一代码风格
- 快速启动开发

---

**使用指南创建时间**: 2025-01-11
**维护人**: 老黑(Claude)
**Agent状态**: ✅ 已完成并部署
**版本**: v1.0
