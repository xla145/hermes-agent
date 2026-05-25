# 项目级原型生成指南

## 核心原则

原型必须是一个**项目级多页面可交互原型**，不能只生成一个巨大的 `prototype.html`，也不能仅用 Tab 隐藏/显示模拟页面。

目标是让用户像体验真实产品一样，通过 URL、导航菜单、按钮、表格操作、详情页入口完成页面跳转和业务流程体验。

## 稳定性优先原则

原型首先必须“能打开、能跳转、能演示”，视觉和动态效果排在稳定性之后。所有生成的原型必须满足：

- 即使 `app.js` 执行失败，主菜单、返回链接、列表详情入口仍应是有效的静态链接。
- 不允许把页面路由能力建立在 JS 注入、hash 路由、Tab 切换或运行时字符串拼接上。
- 不允许只生成一个 HTML 并通过 `showPage()`、`switchTab()`、`display:none` 模拟页面。
- 每个业务页面必须是独立 HTML 文件，能通过浏览器地址栏直接打开。
- 所有页面路径必须使用相对路径，兼容双击打开、VSCode Live Preview、静态服务器和 Cloudflare Pages。

## 视觉一致性原则

原型必须像同一个产品，而不是多个页面拼在一起。生成前先根据 `prototype_plan.json`、原型设计分析文档中的行业、项目类型、核心用户、业务场景和终端约束确定项目级视觉方向，所有页面统一使用。

### 默认视觉风格：简洁专业、逻辑清晰、系统可靠

默认不追求强装饰、强动效和复杂视觉效果，优先保证信息层级清晰、操作路径明确、数据可读性高、状态表达准确、页面密度适中、组件统一、低干扰、低噪音。

允许使用轻量阴影、柔和背景和少量品牌色点缀；禁止为了视觉效果堆叠过多渐变、毛玻璃、强动画、过度装饰和影响可读性的视觉元素。除非用户明确要求或上游计划指定，Glassmorphism、强渐变和深色模式都只能作为可选风格，不作为默认强制项。

### 1. 必须先定义设计令牌

设计令牌必须从 `prototype_design.md` 推导，而不是套用通用后台默认值。推导时至少读取：

- 行业：决定品牌色、语义色和领域组件表达。例如仓储/物流偏高可读、高密度、蓝绿/橙红告警；金融偏稳健、低饱和；教育偏亲和、低压迫。
- 项目类型：B2B 管理后台、移动作业端、数据驾驶舱、C 端应用应有不同视觉密度和组件尺寸。
- 核心用户：一线作业人员优先大字号、大点击区、强状态反馈；运营/管理人员优先表格密度、筛选效率、KPI 和趋势。
- 终端约束：桌面端优先复杂表格和批量操作；PDA/移动端优先单列任务卡片、扫码入口、底部操作区。

在 `assets/css/styles.css` 的 `:root` 中集中定义设计令牌，所有页面和组件只能引用这些变量或由这些变量派生的类：

```css
:root {
  --color-bg: #f5f7fb;
  --color-surface: #ffffff;
  --color-surface-soft: #f8fafc;
  --color-primary: #2563eb;
  --color-primary-hover: #1d4ed8;
  --color-success: #16a34a;
  --color-warning: #d97706;
  --color-danger: #dc2626;
  --color-info: #0891b2;
  --color-text: #111827;
  --color-text-soft: #374151;
  --color-muted: #6b7280;
  --color-border: #e5e7eb;
  --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-md: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 24px;
  --line-height: 1.5;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-page: 28px;
  --space-card: 20px;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --shadow-card: 0 8px 24px rgba(15, 23, 42, 0.06);
  --shadow-modal: 0 24px 64px rgba(15, 23, 42, 0.22);
  --z-sidebar: 20;
  --z-drawer: 40;
  --z-modal: 50;
  --z-toast: 60;
  --duration-fast: 120ms;
  --duration-normal: 180ms;
  --duration-slow: 260ms;
  --focus-ring: 0 0 0 3px rgba(37, 99, 235, 0.18);
  --sidebar-width: 260px;
}
```

禁止在页面中随意硬编码多个不成体系的颜色、圆角、阴影和间距。

### 2. 必须建立统一组件类

`styles.css` 至少应包含并复用以下组件类：

- 布局：`.app`、`.sidebar`、`.main`、`.topbar`、`.content`、`.breadcrumb`
  - 统一骨架必须优先使用 `.app > .sidebar + .main > .topbar + .content`。
  - 如页面生成了兼容别名，CSS 必须显式声明：`.layout` / `.app-layout` 等价 `.app`，`.main-content` 具备 `.main` 的左侧栏避让与 `.content` 的页面内边距能力，避免页面主体压到侧边栏下或无 padding。
- 导航：`.brand`、`.nav-section`、`.nav-link`、`.nav-link.active`
- 容器：`.card`、`.card-header`、`.card-title`、`.card-subtitle`
- 指标：`.metric-card`、`.metric-label`、`.metric-value`、`.metric-trend`
- 表格：`.toolbar`、`.table-wrap`、`table`、`th`、`td`
- 表单：`.form-grid`、`.form-field`、`.input`、`.select`、`.textarea`
- 操作：`.btn`、`.btn-secondary`、`.btn-ghost`、`.btn-danger`
- 状态：`.badge`、`.badge-success`、`.badge-warning`、`.badge-danger`、`.badge-info`
- 反馈：`.toast`、`.empty`、`.loading`、`.skeleton`、`.modal`、`.drawer`、`.alert`
- 业务组件：`.timeline`、`.kanban`、`.chart-card`、`.chart-bars`、`.task-card`、`.location-tag`、`.stock-status`、`.exception-alert`

每类组件必须覆盖可演示状态：hover、focus-visible、disabled、loading、readonly、error、empty。状态样式必须使用统一变量，不允许只靠颜色表达状态，需结合文字、图标、边框或说明。

页面 HTML 应组合这些组件类，不要为每个页面创建一批只用一次的样式。

### 3. 必须体现领域组件

原型不是通用后台换文案，必须根据行业输出领域组件。生成前必须识别行业 / 系统类型，并从下表或 `prototype_plan.json.domainComponents` 中选择领域组件。每个核心模块至少使用 1 个领域组件；核心页面不能全由普通 Card、Table、Form 堆叠而成。

| 行业 / 系统类型 | 必选或优先领域组件 |
|---|---|
| 仓储 / 物流 | 任务卡片、库位标签、库存状态、扫码输入、异常告警、作业时间线、批次 / 效期标记、入库 / 上架 / 拣货 / 复核链路 |
| 生产制造 | 工单卡片、设备状态、产线看板、良率 / 节拍指标、异常停机告警、质检记录、设备维护记录 |
| 审批 / 政务 | 事项卡片、材料清单、流程时间线、审批意见、办理时限、退回原因、办结凭证、受理编号 |
| 财务 / 采购 | 金额摘要、预算占用、付款状态、发票信息、供应商风险、审批轨迹、合同 / 订单关联 |
| 人事 HR | 员工状态、组织架构树、入转调离时间线、审批待办、考勤异常提醒、敏感字段脱敏、绩效周期进度 |
| 客服 / 工单 | 工单优先级、SLA 倒计时、会话时间线、转派 / 升级状态、知识库推荐、客户情绪 / 标签 |
| 电商 / 零售 | 商品卡片、库存 / 售罄标签、价格与促销、订单状态流、售后进度、用户画像、转化漏斗 |
| 数据 / 报表 | 指标卡、趋势图、分布图、筛选口径、数据质量提示、导出记录、权限水印、口径说明 |
| 通用 SaaS | 待办卡片、状态时间线、权限矩阵、操作日志、配置分组、通知中心、审计记录 |

领域组件必须复用统一令牌和组件状态，不允许临时内联样式。每个领域组件至少应包含：业务字段、状态表达、主要操作和异常 / 边界状态。

### 4. 页面布局必须统一

管理后台/SaaS 页面统一采用：

```text
┌────────────┬────────────────────────────────┐
│ Sidebar    │ Topbar                         │
│            ├────────────────────────────────┤
│ Navigation │ Content                        │
│            │  Toolbar / KPI / Card / Table  │
└────────────┴────────────────────────────────┘
```

业务列表页统一结构：

1. 面包屑或页面说明
2. 筛选工具栏 `.toolbar`
3. 数据摘要或 KPI 卡片（如有）
4. 表格 `.table-wrap`
5. 分页/批量操作（如有）

详情页统一结构：

1. 面包屑 + 返回链接
2. 详情摘要卡片
3. 状态流程/时间线
4. 明细表格或关联记录
5. 底部操作区

创建/编辑页统一结构：

1. 面包屑 + 页面说明
2. 分组表单卡片
3. 明细可编辑表格（如有）
4. 底部固定或明确的提交/取消按钮

### 4. UI 组件风格要求

管理后台/SaaS 原型必须引入轻量组件体系，推荐采用 **shadcn/Ant Design 风格的组件语义 + 纯 HTML/CSS 实现**，避免依赖重型前端框架或 CDN 组件库，确保原型可直接静态打开。

必须体现以下组件视觉能力：

- 应用框架：浅色 B2B SaaS 背景、玻璃态/白色侧边栏、统一 Topbar、明确页面标题和说明。
- 品牌与导航：品牌标识、分组导航、当前菜单高亮、hover 状态、菜单项间距统一。
- Card 组件：白色卡片、统一圆角、细边框、柔和阴影、标题/副标题层级清楚。
- KPI 组件：指标标题、主数值、趋势文案、轻量装饰背景，不允许只是普通文本堆叠。
- Button 组件：主按钮、次按钮、危险按钮、幽灵按钮至少覆盖主/次两类，必须有 hover/focus 状态。
- Table 组件：表头底色、行 hover、圆角外框、操作链接样式，表格不能只是默认浏览器样式。
- Form 组件：输入框、选择框、文本域、聚焦态、表单分组和底部操作区统一。
- Badge/Status 组件：成功/进行中/预警/异常/信息类标签使用语义色，不允许全用同一种绿色。
- Feedback 组件：Toast、空状态、加载态、弹窗/确认区至少有可复用样式。
- Chart/Timeline/Kanban 等业务组件必须与整体视觉一致，不能使用临时硬编码风格。

### 5. 视觉密度和风格要求

- 页面背景统一浅灰或品牌渐变，不同页面不要切换风格。
- 卡片圆角、阴影、内边距必须统一。
- 表格表头、hover、边框、操作链接必须统一。
- 所有主要按钮、次要按钮、危险按钮必须统一颜色和 hover 状态。
- 状态标签颜色必须语义化且统一：成功/进行中/预警/异常/禁用。
- 图标必须来自同一风格，优先使用内联 SVG 或统一图标库，禁止 emoji 充当功能图标。
- 页面首屏应有明确重点：管理后台优先展示 KPI、待办、预警、趋势或核心列表。
- 禁止输出压缩成一行的 CSS；`styles.css` 应保持可读、可维护，便于用户继续调整视觉。

### 5. 响应式一致性

- 1024px 以下侧边栏可折叠为抽屉。
- 768px 以下 KPI 卡片、表单、表格工具栏应垂直排列。
- 表格允许横向滚动，但不能破坏页面整体宽度。
- 所有页面响应式行为必须一致，不能某些页面有移动端适配、某些没有。

## 输出目录结构

默认输出到 `prototype/` 目录：

```text
prototype/
├── index.html                 # 入口页，通常为登录页或工作台入口
├── README.md                  # 原型说明、页面路由清单、使用方式
├── assets/
│   ├── css/
│   │   └── styles.css         # 公共样式、主题变量、组件样式
│   ├── js/
│   │   ├── app.js             # 公共导航、权限模拟、toast、modal 等
│   │   └── mock-data.js       # 模拟数据
│   └── images/                # 图片资源，如有需要
└── pages/
    ├── dashboard.html         # 工作台/首页
    ├── login.html             # 登录页，如 index.html 不作为登录页时使用
    ├── xxx-list.html          # 列表页
    ├── xxx-detail.html        # 详情页
    ├── xxx-create.html        # 创建页
    └── settings.html          # 设置/权限等页面
```

如产品是管理后台/SaaS，推荐 `index.html` 作为登录页，登录成功跳转 `pages/dashboard.html`。

## 路由与跳转要求

### 1. 必须提供真实页面跳转

使用普通链接或 JS 跳转：

```html
<a href="./inventory.html">库存查询</a>
<a href="./inventory-detail.html?id=SKU-001">查看详情</a>
<button onclick="location.href='./inbound-create.html'">新建入库单</button>
```

**路径规则（强制）**：

- `index.html` 位于 `prototype/` 根目录，跳转到业务页必须使用 `./pages/xxx.html`。
- `pages/*.html` 位于 `prototype/pages/` 目录，页面之间互跳必须使用 `./xxx.html`，不要写 `./pages/xxx.html`、`../pages/xxx.html` 或依赖当前 URL 字符串拼接。
- 主导航必须在每个业务 HTML 页面中写成静态 `<a href="./xxx.html">`，不能由 JS 拼接或注入。
- 业务页面中的按钮跳转也必须遵守相同规则：在 `pages/*.html` 中跳转详情页写 `location.href='./inventory-detail.html?id=SKU-001'`。
- 详情页、创建页、编辑页的侧边栏菜单可以通过 `data-route` 指向所属一级模块，例如 `data-page="inbound-detail"` 时，入库菜单使用 `data-route="inbound"` 高亮。

推荐业务页静态外壳：

```html
<body data-page="inventory-detail">
  <div class="app">
    <aside class="sidebar" id="sidebar">
      <div class="brand"><span class="brand-mark">W</span><span>产品名</span></div>
      <nav class="sidebar-nav">
        <a href="./dashboard.html" class="nav-link" data-route="dashboard">工作台</a>
        <a href="./inventory.html" class="nav-link" data-route="inventory">库存查询</a>
        <a href="./inbound-list.html" class="nav-link" data-route="inbound">入库管理</a>
      </nav>
    </aside>
    <main class="main">
      <header class="topbar">
        <button type="button" onclick="toggleSidebar()">菜单</button>
        <div class="page-title">
          <h1 id="page-title-text">页面标题</h1>
          <p id="page-subtitle-text">页面说明</p>
        </div>
      </header>
      <section class="content" id="page-content"></section>
    </main>
  </div>
  <script src="../assets/js/mock-data.js"></script>
  <script src="../assets/js/app.js"></script>
  <script>renderInventoryDetail();</script>
</body>
```

禁止只使用：

```js
showPage('inventory')
switchTab('page-a')
```

Tab 可以用于同一页面内部的局部内容切换，但不能代替产品级页面路由。

### 2. README 必须包含路由清单

`prototype/README.md` 必须列出每个页面的路径、页面名称、入口和说明：

```markdown
# 原型路由清单

| 路径 | 页面 | 说明 | 入口 |
|-----|------|------|------|
| index.html | 登录页 | 用户登录系统 | 直接打开 |
| pages/dashboard.html | 工作台 | 查看运营总览 | 登录成功后进入 |
| pages/inventory.html | 库存查询 | 查询库存与库存状态 | 左侧菜单 |
| pages/inventory-detail.html?id=SKU-001 | 库存详情 | 查看库存流水 | 库存列表“查看” |
```

### 3. 导航必须全局一致

管理后台类原型应有统一布局：

- 顶部栏：产品名、当前页面标题、用户信息、快捷操作
- 侧边栏：一级/二级菜单
- 内容区：页面主体
- 面包屑：复杂业务页面建议添加

每个业务页面都应复用相同导航结构，并高亮当前菜单。

### 4. 业务操作必须形成链路

不能只展示静态页面。关键业务应能从入口一路点击到结果页或详情页。

示例：仓储系统

```text
登录页 index.html
  → 工作台 pages/dashboard.html
  → 库存查询 pages/inventory.html
  → 库存详情 pages/inventory-detail.html?id=SKU-AX239

工作台 pages/dashboard.html
  → 入库单列表 pages/inbound-list.html
  → 新建入库 pages/inbound-create.html
  → 入库详情 pages/inbound-detail.html?id=IN-001
  → 上架确认 pages/putaway-confirm.html?id=TASK-001

任务看板 pages/tasks.html
  → 任务详情 pages/task-detail.html?id=T-10021
  → 异常处理 pages/exception-detail.html?id=E-001
```

## 页面完成度要求

原型不能只做“看起来像页面”的静态列表。每类页面都必须达到可演示、可验收的完成定义。

### 0. 页面落地价值要求

每个核心页面在生成前必须明确：

- 用户到这个页面要完成的核心任务。
- 首屏必须让用户看到的关键信息。
- 用户最常用的 3 个操作。
- 页面判断业务是否正常的依据。
- 必须体现的数据细节。
- 必须体现的异常 / 边界场景。
- 该页面不能只做成普通表格或普通表单的原因。

生成页面时必须把这些内容体现在页面结构、字段、操作、状态和 Mock 数据中。

### 1. 列表页完成定义

每个核心列表页必须包含：

- 真实静态入口：左侧菜单或工作台快捷入口可进入。
- 页面说明/面包屑：用户知道当前模块和用途。
- 筛选工具栏：至少包含关键词、状态/类型筛选、查询、重置。
- 数据表格：不少于 4 条模拟数据，覆盖正常、进行中、预警、异常等状态。
- 行内操作：至少包含“查看详情”，如适用还应包含“编辑/处理/审批/删除/导出”。
- 新建入口：如模块支持创建，必须有 `新建` 按钮跳转独立创建页。
- 分页/批量操作：数据类后台列表必须展示分页或批量操作区域。
- 空状态：通过静态结构或 JS 演示无数据时的提示。

### 2. 详情页完成定义

每个核心详情页必须包含：

- 返回列表的静态链接。
- 摘要信息卡：编号、状态、负责人、时间等关键字段。
- 状态流程/时间线：展示当前节点和历史流转。
- 明细表格或关联数据：如商品明细、审批记录、库存流水、操作日志。
- 底部操作区：根据状态展示处理、提交、取消、返回等按钮。
- URL 参数读取：能通过 `?id=xxx` 展示或至少保留对应编号。

### 3. 创建/编辑页完成定义

每个创建/编辑页必须包含：

- 分组表单：基础信息、业务明细、备注/附件等分组。
- 必填项标识和基础校验。
- 明细行增删改：如订单/入库/商品类页面必须展示可编辑明细表格。
- 取消按钮：静态返回上级页面。
- 提交按钮：有 loading/Toast/成功跳转或成功反馈。

### 4. 执行/审批页完成定义

任务、审批、扫码、复核等流程页必须包含：

- 当前任务/审批对象摘要。
- 步骤说明或进度条。
- 核心执行控件：扫码输入框、确认按钮、审批意见、异常上报等。
- 成功、失败、异常三类反馈展示。
- 完成后跳转详情或任务列表。

### 5. 报表/分析页完成定义

报表页必须包含：

- KPI 指标卡。
- 筛选条件：日期范围、组织/仓库/类型等。
- 图表占位或 CSS 图表。
- 明细表格。
- 导出按钮和导出反馈。

### 6. 设置/权限页完成定义

系统设置页必须包含：

- 设置分组导航。
- 参数表单或权限矩阵。
- 保存按钮和反馈。
- 至少一个危险操作或敏感配置的二次确认示例。

## 页面数量要求

根据产品复杂度生成足够页面，不要只做 3-5 个泛化页面。

### 管理后台 / SaaS 推荐最小页面集

- 登录页
- 工作台 / 数据总览
- 至少 3 个核心业务模块列表页
- 至少 2 个详情页
- 至少 1 个创建/编辑表单页
- 至少 1 个报表/分析页
- 至少 1 个系统设置或权限页

### 电商/用户端推荐最小页面集

- 首页
- 登录/注册页
- 列表/搜索页
- 详情页
- 购物车/确认页
- 订单页
- 个人中心

### 移动端推荐最小页面集

- 启动/登录页
- 首页
- 核心流程页 3 个以上
- 详情页
- 我的/设置页

## 技术规格

使用静态 HTML/CSS/JS，便于直接打开或部署：

- HTML 多页面
- 默认使用项目级纯 CSS 组件体系，不默认依赖 Tailwind CDN
- 只有用户明确要求 Tailwind，或目标项目本身已采用 Tailwind 时，才允许引入 Tailwind CDN
- 原生 JS
- 公共样式抽离到 `assets/css/styles.css`
- 公共交互抽离到 `assets/js/app.js`
- 模拟数据抽离到 `assets/js/mock-data.js`

默认不使用 Tailwind 的原因：静态原型需要可离线打开；统一 CSS Variables + 组件类更利于维护和验收；避免 Tailwind 工具类与项目组件类混杂导致风格漂移。

## 资源拆分强制要求

除极少量页面初始化调用外，禁止在 HTML 页面中写大量内联 `<style>` 或 `<script>`。默认不插入 Tailwind CDN；只有用户明确要求或项目已采用 Tailwind 时才允许出现。

必须拆分为：

- `assets/css/styles.css`：主题变量、布局、组件样式、响应式补充、动画、状态样式
- `assets/js/app.js`：公共导航、菜单高亮、Toast、Modal、表单校验、Loading、通用跳转、URL 参数读取
- `assets/js/mock-data.js`：跨页面共享模拟数据，例如库存、订单、任务、用户、报表数据
- `pages/*.html`：只负责页面结构、语义化内容、表单和按钮入口
- `index.html`：只负责入口页结构，例如登录页、欢迎页或项目入口

允许每个 HTML 页面保留极少量初始化代码，例如：

```html
<script>
  initPage('inventory');
  renderInventoryTable();
</script>
```

但业务逻辑、列表渲染逻辑、表单提交逻辑、弹窗逻辑、筛选逻辑必须放在 JS 文件中。

不要生成这种结构：

```html
<style>
  /* 大量页面样式 */
</style>
<script>
  // 大量业务逻辑
</script>
```

应该生成这种结构：

```html
<link rel="stylesheet" href="../assets/css/styles.css">
<script src="../assets/js/mock-data.js"></script>
<script src="../assets/js/app.js"></script>
```

页面引用示例：

```html
<link rel="stylesheet" href="../assets/css/styles.css">
<script src="../assets/js/mock-data.js"></script>
<script src="../assets/js/app.js"></script>
```

`index.html` 位于根目录时，资源路径应使用：

```html
<link rel="stylesheet" href="./assets/css/styles.css">
<script src="./assets/js/app.js"></script>
```

`pages/*.html` 引用资源时，路径应使用：

```html
<link rel="stylesheet" href="../assets/css/styles.css">
<script src="../assets/js/app.js"></script>
```

## 设计风格选项

以下风格为可选项。默认使用“简洁专业 B2B/SaaS 风格”，仅在用户明确要求、上游 `prototype_plan.json` 指定或项目定位确实需要时采用更强视觉风格。

### 1. Glassmorphism（毛玻璃）
- 半透明背景 + 模糊效果
- `backdrop-blur-lg bg-white/30`

### 2. Minimalism（极简）
- 大量留白 + 清晰层次
- 黑白灰为主 + 单色点缀

### 3. Material Design
- 卡片阴影 + 圆角
- `shadow-md rounded-lg`

### 4. Dark Mode（深色模式）
- 深色背景 + 亮色文字
- `bg-gray-900 text-white`

## 必备交互组件

### 1. 全局导航

**强制要求：主导航必须写在每个 HTML 页面里，禁止依赖 JS 动态生成主导航。**

原因：静态原型常被直接双击打开、用 VSCode Live Preview 打开或部署到不同静态路径下；如果主导航依赖 JS 注入，一旦 JS 路径、缓存、执行顺序或预览环境异常，菜单会整块失效。

`pages/*.html` 中推荐写法：

```html
<aside class="sidebar">
  <a href="./dashboard.html" data-route="dashboard">工作台</a>
  <a href="./inventory.html" data-route="inventory">库存查询</a>
  <a href="./tasks.html" data-route="tasks">任务看板</a>
</aside>
```

`index.html` 中跳转业务页必须写：

```html
<a href="./pages/dashboard.html">进入工作台</a>
```

当前菜单高亮可通过每页设置：

```html
<body data-page="inventory">
```

```js
const page = document.body.dataset.page || 'dashboard';
const current = page.split('-')[0];
document.querySelectorAll('[data-route]').forEach(link => {
  link.classList.toggle('active', link.dataset.route === current);
});
```

### 2. 表单校验

```javascript
function validateRequired(form) {
  const invalid = [...form.querySelectorAll('[required]')].find(input => !input.value.trim());
  if (invalid) {
    showToast('请完整填写必填项', 'error');
    invalid.focus();
    return false;
  }
  return true;
}
```

### 3. Loading 状态

```javascript
function submitWithLoading(btn, callback) {
  const originalText = btn.textContent;
  btn.disabled = true;
  btn.textContent = '提交中...';
  setTimeout(() => {
    btn.disabled = false;
    btn.textContent = originalText;
    callback && callback();
  }, 600);
}
```

### 4. Toast 提示

```javascript
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2400);
}
```

### 5. 模态框/抽屉

模态框和抽屉用于单页内轻量操作，例如确认删除、快速筛选、备注填写。详情、创建、审批等复杂流程应使用独立页面。

## 视觉打磨要求

原型必须达到「可演示给客户或老板」的视觉水准，不能看起来像未完成的 wireframe。视觉打磨服务于信息表达和业务演示，不应牺牲简洁性、可读性和系统可靠性。以下是具体的视觉打磨要求：

### 1. 行业化配色

禁止直接使用默认蓝 `#2563eb`。必须根据行业推导差异化主色：

| 行业 | 主色方向 | 辅色 | 告警色 | 说明 |
|------|---------|------|--------|------|
| 仓储/物流/制造 | 钢蓝 #3b82f6 → #1e40af | 橙色 #f59e0b | 红 #ef4444 | 工业、可靠、高效 |
| 金融/保险 | 深蓝 #1e3a5f + 金色点缀 | 绿 #059669 | 红 #dc2626 | 稳健、信任 |
| 教育/培训 | 紫色 #7c3aed + 暖橙 #fb923c | 蓝绿 #0d9488 | 橙 #ea580c | 活力、亲和 |
| 医疗/健康 | 蓝绿 #0d9488 + 白 | 浅蓝 #38bdf8 | 红 #dc2626 | 专业、洁净 |
| 电商/零售 | 品红/品牌色 + 橙色促销 | 绿 #22c55e | 红 #dc2626 | 活力、转化 |
| 政府/公共 | 藏蓝 #1e3a5f + 红点缀 | 灰蓝 | 红标 | 正式、权威 |
| 通用 SaaS | 中性蓝 #4f46e5 + 紫渐变 | 灰绿 | 红标 | 现代、科技 |

调色板必须包含至少 12 个语义色变量：primary、primary-hover、primary-soft、success、warning、danger、info、bg、surface、text、text-soft、muted、border。

### 2. 侧边栏视觉品质

侧边栏是原型的视觉锚点，不能是简单的无层次链接列表。默认采用简洁浅色侧边栏；如项目风格需要，可采用以下增强方案之一：

**方案A：轻量毛玻璃侧边栏（可选）**
```css
.sidebar {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 4px 0 24px rgba(15, 23, 42, 0.04);
}
```

**方案B：深色侧边栏**
```css
.sidebar {
  background: linear-gradient(180deg, #0f172a, #1e293b);
  color: #e2e8f0;
}
.sidebar .nav-link { color: #94a3b8; }
.sidebar .nav-link:hover { color: #fff; background: rgba(255,255,255,0.08); }
.sidebar .nav-link.active { color: #fff; background: rgba(255,255,255,0.12); }
```

品牌 Logo 区域应有清晰识别度，可使用简洁字母 / 图标标识和轻量品牌色点缀。

### 3. 卡片深度与层次

卡片应体现清晰层次，可使用细边框、轻量阴影和一致内边距：
```css
.card {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(15, 23, 42, 0.06);
  padding: 24px;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(15, 23, 42, 0.1);
}
```

### 4. 按钮质感

主按钮应有明确主次层级，可使用实色或轻量渐变；不应使用过强阴影：
```css
.primary-btn {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-weight: 700;
  transition: all 180ms ease;
}
.primary-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
}
```

### 5. KPI 指标卡装饰

指标卡不能只是文字堆叠，必须有清晰的信息层级：
- 主数值应突出显示，字号和字重明显高于说明文字
- 趋势使用语义色 + 箭头符号或文字说明
- 不同指标可使用轻量装饰色，但不能影响可读性
- 如使用圆形渐变装饰，应保持克制、低透明度

### 6. 表格精致度

```css
.data-table {
  border-collapse: separate;
  border-spacing: 0;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  overflow: hidden;
}
.data-table th {
  background: rgba(248, 250, 252, 0.9);
  font-weight: 700;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-muted);
}
.data-table tbody tr {
  transition: background 120ms ease;
}
.data-table tbody tr:hover {
  background: #f0f7ff;
}
```

操作链接使用标签样式而非裸文字：
```css
.table-action {
  display: inline-flex;
  padding: 4px 10px;
  border-radius: 6px;
  background: rgba(37, 99, 235, 0.08);
  color: var(--color-primary);
  font-weight: 700;
}
```

### 7. 微交互

所有可交互元素应有轻量过渡反馈：
```css
/* 统一过渡 */
.nav-link, .btn, .card, .table-action, .badge {
  transition: all 180ms ease;
}

/* 导航 hover 位移 */
.nav-link:hover { transform: translateX(2px); }

/* 表单聚焦光晕 */
input:focus, select:focus, textarea:focus {
  border-color: rgba(37, 99, 235, 0.6);
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
}
```

### 8. 页面背景

页面背景应避免单调无层次，可使用浅灰底、极淡品牌色块或低透明度渐变：
```css
body {
  background: radial-gradient(circle at top left, rgba(37, 99, 235, 0.12), transparent 35%),
              linear-gradient(135deg, var(--color-bg), #eef4ff 50%, var(--color-bg));
}
```

### 9. 空状态品质

空状态不能只是灰色文字，应包含简洁图形或装饰元素、原因说明和操作引导按钮。

## 响应式适配

每个页面必须考虑：

- 375px 移动宽度
- 768px 平板宽度
- 1024px 小桌面
- 1440px 大桌面

管理后台在移动端可以将侧边栏收起为抽屉。

```html
<button class="md:hidden" onclick="toggleSidebar()" aria-label="打开导航">
  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
  </svg>
</button>
```

## 模拟数据

模拟数据应服务于多个页面共享，不要散落在每个 HTML 中。Mock 数据不是占位文案，而是让原型具备业务演示价值的关键资产。

### 1. 数据量和状态覆盖

每个核心业务实体默认至少包含 8 条列表数据，除明显不适用外必须覆盖：

- 正常数据：展示业务稳定运行状态。
- 进行中数据：展示流程正在处理。
- 预警数据：展示接近阈值、即将超期、库存不足、风险升高等状态。
- 异常数据：展示失败、驳回、超期、缺资料、冲突、不可执行等状态。
- 完成 / 关闭数据：展示流程闭环。
- 边界数据：例如金额为 0、库存为 0、缺附件、审批被驳回、负责人为空、超 SLA、批次临期等。

### 2. 跨页面数据关系

列表页、详情页、审批页、报表页和工作台必须尽量引用同一批业务对象 ID。不要每个页面各写一套互不相关的数据。推荐结构：

```javascript
window.MockData = {
  inventory: [
    { id: 'SKU-001', name: '智能温控传感器', location: 'A-R01-L01-02', available: 86, status: '预警', batchNo: 'B20260501', owner: '张工' }
  ],
  inventoryFlows: [
    { id: 'F-001', skuId: 'SKU-001', action: '入库', quantity: 120, operator: '李工', time: '2026-05-17 09:30' }
  ],
  tasks: [
    { id: 'T-10021', businessId: 'SKU-001', type: '上架', assignee: '张工', status: '进行中' }
  ],
  operationLogs: [
    { id: 'LOG-001', businessId: 'SKU-001', action: '库存预警确认', operator: '王主管', time: '2026-05-17 10:10' }
  ]
};
```

### 3. 详情页数据深度

详情页不能只展示主表字段，必须至少包含以下三类关联数据：

- 明细表格，例如商品明细、材料明细、人员明细、费用明细。
- 状态流转 / 时间线。
- 操作日志 / 审计记录。
- 附件 / 备注 / 审批意见。
- 关联对象，例如客户、供应商、部门、仓库、设备、合同、订单。

### 4. 页面状态数据

Mock 数据必须支撑页面展示默认态、加载态、空数据态、错误态、无权限态、成功态和失败态中的主要场景。空状态可以用独立空数组或筛选后无结果演示，但不能只有一句“暂无数据”。

详情页可通过 URL 参数读取模拟数据：

```javascript
const params = new URLSearchParams(location.search);
const id = params.get('id');
```

## 原型验收交付要求

交付时必须产出验收结果，不能只说“已生成”。

### 生成后强制自检：CSS 类完整性

在写完 HTML/CSS/JS 后，必须检查页面中使用的类名是否在 `assets/css/styles.css` 中存在对应定义。重点不是所有原子状态类都必须独立定义，而是会影响页面显示和交互的布局/组件/显隐类必须定义。

必须覆盖以下检查：

1. **显隐类**：Tab/Section 类必须有 display 控制，例如：
   ```css
   .report-panel { display: none; }
   .report-panel.active { display: block; }
   .settings-section { display: none; }
   .settings-section.active { display: block; }
   ```
2. **布局类**：页面使用的 `app`、`layout`、`app-layout`、`main`、`main-content`、`content`、`kanban-board`、`location-grid`、`metrics-row`、`metric-row`、`panel-grid`、`settings-layout` 等必须在 CSS 中定义 grid/flex、左侧栏避让和页面 padding。
3. **业务组件类**：库位卡片、任务看板、扫码输入、报表图表、时间线、步骤条等领域组件类必须有样式，不能只依赖浏览器默认样式。
4. **状态级联类**：如果 HTML 写成 `<div class="timeline-step done"><div class="timeline-dot"></div></div>`，CSS 必须定义 `.timeline-step.done .timeline-dot`，不能只定义 `.timeline-dot.done`。
5. **JS/HTML 类名一致**：JS 查询选择器必须兼容 HTML 实际类名，例如页面用 `.kanban-col-count`，JS 不得只查询 `.kanban-count`。
6. **骨架别名一致性**：如果任一页面使用 `.layout`、`.app-layout`、`.main-content`，必须在 `styles.css` 中补齐兼容定义；更推荐统一替换为 `.app`、`.main`、`.content`，不要同一原型内随机混用。
7. **表单/按钮别名类**：如果页面使用 `form-input`、`form-textarea`、`input-sm`、`form-input-sm`、`btn-link`、`btn-dashed` 等类，CSS 必须补齐；不要混用两套类名而只定义其中一套。

可使用类似下面的检查思路（也可手工检查）：

```bash
# 检查 HTML 使用的 class 是否可能缺少 CSS 定义
node -e "
const fs=require('fs');
const css=fs.readFileSync('prototype/assets/css/styles.css','utf8');
const files=fs.readdirSync('prototype/pages').map(f=>'prototype/pages/'+f).concat(['prototype/index.html']);
const used=new Set();
for (const file of files) {
  const html=fs.readFileSync(file,'utf8');
  for (const m of html.matchAll(/class=\"([^\"]+)\"/g)) {
    m[1].split(/\s+/).forEach(c=>used.add(c));
  }
}
const ignore=new Set(['active','done','pending','open','loading','error','success','warning','danger','info','primary','muted','up','down','overdue']);
const missing=[...used].filter(c=>!ignore.has(c) && !css.includes('.'+c));
console.log(missing.join('\n'));
"
```

如果发现缺失类，必须先补齐 `styles.css`，再生成/更新 `validation-report.md`。

### 必须生成或更新的验收文件

- `prototype/README.md`：路由清单、页面说明、主要业务链路、使用方式。
- `generation-report.md`：生成摘要、任务完成情况、校验状态、文件清单。
- `validation-report.md`：机器/人工验收项、错误、警告、未完成项、建议。

### 验收报告必须覆盖

1. **任务完成度**：规划中的页面和业务链路是否完成。
2. **路由完整性**：所有 `href` 指向的本地 HTML 是否存在。
3. **页面类型覆盖**：登录、工作台、列表、详情、创建/编辑、执行/审批、报表、设置是否覆盖。
4. **核心交互覆盖**：筛选、重置、查看、创建、提交、返回、Toast、空状态、加载状态是否覆盖。
5. **资源拆分**：CSS、JS、mock data 是否拆分。
6. **视觉一致性**：是否使用统一设计令牌和组件类。
7. **CSS 类完整性**：HTML 中影响布局、显隐、组件展示的类是否都在 `styles.css` 中定义；Tab/Section 是否有 `.active` 显隐样式；JS 查询类名是否与 HTML 一致。
8. **组件状态覆盖**：hover、focus-visible、disabled、loading、readonly、error、empty 是否有统一样式和页面示例。
9. **无障碍风险**：表单 label、键盘焦点、颜色对比、状态是否只依赖颜色。
10. **响应式完整性**：1024px、768px、375px 下布局、表格和操作区是否可用。
11. **限制说明**：仍是静态原型，哪些动作是模拟数据或前端演示。

### 验收输出格式

```markdown
# 原型验收报告

## 验收结论
- 状态：通过 / 有警告 / 不通过

## 任务完成度
| 任务 | 状态 | 说明 |
|------|------|------|

## 页面覆盖
| 页面类型 | 是否覆盖 | 页面路径 |
|---------|----------|----------|

## 业务链路验证
| 链路 | 结果 | 说明 |
|------|------|------|

## 问题与建议
- [警告/缺陷] 描述 → 建议
```

## 原型质量检查

交付前必须检查：

- [ ] 是否输出 `prototype/` 目录，而不是单个 HTML 文件
- [ ] 是否有 `index.html` 作为项目入口
- [ ] 是否有 `pages/` 子页面目录
- [ ] 是否将公共 CSS 拆分到 `assets/css/styles.css`
- [ ] 是否将公共 JS 拆分到 `assets/js/app.js`
- [ ] 主导航是否写在每个 `pages/*.html` 页面中，而不是由 JS 动态生成
- [ ] 是否将模拟数据拆分到 `assets/js/mock-data.js`
- [ ] HTML 中是否避免大量内联 `<style>` 和 `<script>`
- [ ] 是否有 `README.md` 路由清单
- [ ] 是否至少覆盖核心业务流程的入口、列表、详情、创建/处理页
- [ ] 所有菜单和按钮是否有真实跳转或明确交互
- [ ] 页面之间资源路径是否正确
- [ ] 当前菜单是否能高亮
- [ ] 从 `prototype/index.html` 登录/入口能否跳转到 `pages/dashboard.html`
- [ ] 在每个 `pages/*.html` 页面点击左侧菜单，是否都能跳到正确页面
- [ ] `pages/*.html` 内部的列表查看、详情、创建、返回等链接是否使用 `./xxx.html`，没有误写成 `./pages/xxx.html`
- [ ] 使用浏览器 DevTools Console 检查是否无 `ReferenceError`、`SyntaxError` 等导致导航 JS 中断的错误
- [ ] 是否有空状态、加载状态、错误提示
- [ ] 是否不使用 emoji 作为图标，而使用 SVG 或统一图标库
- [ ] 所有可点击元素是否有 `cursor-pointer`
- [ ] Hover 状态是否有清晰反馈且不导致布局偏移
- [ ] 焦点状态是否可见
- [ ] 是否尊重 `prefers-reduced-motion`
- [ ] 亮/暗模式文字对比度是否达标
