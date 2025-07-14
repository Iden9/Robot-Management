# 宇树G1 EDU机器人管理系统 - 前端

基于 Vue 3 + Vite 构建的现代化机器人管理系统前端应用，为宇树G1 EDU机器人提供完整的管理界面和控制功能。

## 📋 项目简介

本项目是宇树G1 EDU机器人管理系统的前端部分，提供直观易用的Web界面，支持设备管理、教育培训、自主导览、系统监控等核心功能。采用现代化的前端技术栈，确保良好的用户体验和系统性能。

## 🚀 技术栈

- **框架**: Vue 3.5.17 (Composition API)
- **构建工具**: Vite 7.0.0
- **路由**: Vue Router 4.5.1
- **状态管理**: Pinia 3.0.3
- **HTTP客户端**: Axios 1.10.0
- **开发工具**: Vue DevTools 7.7.7
- **语言**: JavaScript (ES6+)
- **样式**: CSS3 + 响应式设计

## 🏗️ 项目结构

```
front/
├── public/                 # 静态资源
│   └── favicon.ico
├── src/
│   ├── api/               # API接口定义
│   │   ├── auth.js        # 认证相关API
│   │   ├── equipment.js   # 设备管理API
│   │   ├── education.js   # 教育培训API
│   │   ├── navigation.js  # 导览管理API
│   │   └── ...
│   ├── components/        # 可复用组件
│   │   ├── dashboard/     # 仪表板组件
│   │   ├── equipment/     # 设备管理组件
│   │   ├── education/     # 教育培训组件
│   │   ├── navigation/    # 导览组件
│   │   ├── account/       # 账户管理组件
│   │   └── settings/      # 系统设置组件
│   ├── stores/            # Pinia状态管理
│   │   ├── auth.js        # 认证状态
│   │   ├── equipment.js   # 设备状态
│   │   ├── dashboard.js   # 仪表板状态
│   │   └── ...
│   ├── views/             # 页面组件
│   │   ├── Login/         # 登录页面
│   │   ├── SystemDashboard/ # 系统仪表板
│   │   ├── EquipmentManagement/ # 设备管理
│   │   ├── EducationTraining/ # 教育培训
│   │   ├── SelfGuidedNavigation/ # 自主导览
│   │   ├── AccountManagement/ # 账户管理
│   │   ├── SystemSettings/ # 系统设置
│   │   └── RobotControl/  # 机器人控制
│   ├── router/            # 路由配置
│   ├── utils/             # 工具函数
│   ├── config/            # 配置文件
│   ├── directives/        # 自定义指令
│   ├── App.vue            # 根组件
│   └── main.js            # 应用入口
├── index.html             # HTML模板
├── vite.config.js         # Vite配置
├── package.json           # 项目依赖
└── README.md              # 项目文档
```

## ✨ 功能模块

### 🔐 用户认证
- 用户登录/注册
- JWT Token认证
- 权限控制和路由守卫
- 用户信息管理

### 📊 系统仪表板
- 设备状态总览
- 实时监控数据
- 系统运行状态
- 快捷操作面板

### 🤖 设备管理
- 设备列表查看
- 设备信息编辑
- 设备状态监控
- 批量设备导入
- 设备数据导出

### 📚 教育培训
- 课件管理
- 课件上传/下载
- 课件预览
- 培训内容分类

### 🗺️ 自主导览
- 导览路线配置
- 地图管理
- 导览任务调度
- 路径规划

### 👥 账户管理
- 用户管理
- 角色权限管理
- 用户操作日志

### ⚙️ 系统设置
- 服务器配置
- 通知设置
- 安全配置
- 数据备份管理

### 🎮 机器人控制
- 实时控制界面
- 动作指令发送
- 状态反馈显示

## 🛠️ 开发环境设置

### 环境要求

- Node.js >= 16.0.0
- pnpm >= 7.0.0 (推荐) 或 npm >= 8.0.0

### 安装依赖

```bash
# 使用 pnpm (推荐)
pnpm install

# 或使用 npm
npm install
```

### 开发服务器

```bash
# 启动开发服务器
pnpm dev

# 或
npm run dev
```

访问 http://localhost:5173 查看应用

### 构建生产版本

```bash
# 构建生产版本
pnpm build

# 或
npm run build
```

### 预览生产版本

```bash
# 预览构建结果
pnpm preview

# 或
npm run preview
```

## 🔧 配置说明

### API代理配置

开发环境下，API请求会自动代理到后端服务器：

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5001',
      changeOrigin: true,
    },
  },
}
```

### 环境变量

可以创建 `.env.local` 文件来配置环境变量：

```bash
# API基础URL
VITE_API_BASE_URL=http://localhost:5001

# 应用标题
VITE_APP_TITLE=宇树G1 EDU机器人管理系统
```

## 🎨 开发指南

### 代码规范

- 使用 Vue 3 Composition API
- 组件命名采用 PascalCase
- 文件命名采用 kebab-case
- 使用 ESLint 进行代码检查

### 组件开发

```vue
<template>
  <div class="component-name">
    <!-- 模板内容 -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 组件逻辑
const data = ref(null)

const computedValue = computed(() => {
  return data.value ? data.value.processed : null
})

onMounted(() => {
  // 初始化逻辑
})
</script>

<style scoped>
.component-name {
  /* 样式定义 */
}
</style>
```

### 状态管理

使用 Pinia 进行状态管理：

```javascript
// stores/example.js
import { defineStore } from 'pinia'

export const useExampleStore = defineStore('example', {
  state: () => ({
    data: null,
    loading: false
  }),
  
  getters: {
    processedData: (state) => {
      return state.data ? state.data.processed : null
    }
  },
  
  actions: {
    async fetchData() {
      this.loading = true
      try {
        // API调用
        this.data = await api.getData()
      } finally {
        this.loading = false
      }
    }
  }
})
```

## 🚀 部署指南

### Docker部署

```bash
# 构建Docker镜像
docker build -t robot-management-frontend .

# 运行容器
docker run -p 80:80 robot-management-frontend
```

### Nginx配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔍 推荐IDE设置

- **编辑器**: [VSCode](https://code.visualstudio.com/)
- **插件**: 
  - [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (Vue 3支持)
  - [TypeScript Vue Plugin](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin)
  - 禁用 Vetur 插件以避免冲突

## 📚 相关文档

- [Vue 3 官方文档](https://vuejs.org/)
- [Vite 配置参考](https://vitejs.dev/config/)
- [Vue Router 文档](https://router.vuejs.org/)
- [Pinia 状态管理](https://pinia.vuejs.org/)
- [Axios HTTP客户端](https://axios-http.com/)

**宇树G1 EDU机器人管理系统** - 让机器人管理更简单、更智能
