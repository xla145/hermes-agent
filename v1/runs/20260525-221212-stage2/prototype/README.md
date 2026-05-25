# 广西贵港农贸市场实时现货交易平台静态原型

## 使用方式
直接打开 `prototype/index.html`，或打开 `prototype/pages/*.html`。所有导航为静态链接，JS仅增强Toast、筛选、弹窗、表单校验。

## 路由清单
| 路径 | 页面 | 页面类型 | 说明 | 入口 |
|---|---|---|---|---|
| index.html | 登录页 | 登录/权限页 | 身份认证与角色分流 | 直接打开 |
| pages/dashboard.html | PC工作台 | 工作台 | 角色化展示待办和指标 | T002 |
| pages/mobile-home.html | 移动端首页 | 工作台 | 移动端快捷入口 | T003 |
| pages/account-register.html | 主体注册申请页 | 新增页 | 提交主体入驻资料 | T004 |
| pages/account-audit-list.html | 主体审核列表 | 审批页 | 管理待审核主体 | T005 |
| pages/account-audit-detail.html | 主体审核详情 | 审批页 | 查看资质并完成审核 | T006 |
| pages/subject-management.html | 主体管理列表与详情 | 列表/详情页 | 主体档案维护与监管 | T007 |
| pages/account-binding-deposit.html | 账户绑定与保证金账户页 | 配置/详情页 | 完成账户绑定和保证金管理 | T008 |
| pages/source-entry.html | 溯源录入页组 | 新增/编辑页 | 完成产地/加工/仓储/运输录入 | T009 |
| pages/source-archive-list.html | 溯源档案列表 | 列表页 | 查询管理溯源档案 | T010 |
| pages/source-archive-detail.html | 溯源档案详情 | 详情页 | 展示全流程溯源链路 | T011 |
| pages/mini-trace.html | 小程序溯源查询与结果页 | 查询/详情页 | 消费者扫码查看公开溯源 | T012 |
| pages/source-audit-warning.html | 溯源审核与预警中心 | 审批/列表页 | 审核溯源和处理异常 | T013 |
| pages/source-template.html | 溯源模板管理页 | 配置页 | 管理录入模板 | T014 |
| pages/trade-listing.html | 挂单列表与新增挂单页 | 列表/新增页 | 管理商户挂单 | T015 |
| pages/trade-listing-audit.html | 挂单审核页 | 审批页 | 审核挂单合规性 | T016 |
| pages/trade-market-order-confirm.html | 挂单市场与下单确认页 | 列表/新增页 | 采购商筛选挂单并下单 | T017 |
| pages/trade-match.html | 平台撮合页 | 列表页 | 支持平台匹配与批量撮合 | T018 |
| pages/order-list-detail.html | 订单列表与订单详情 | 列表/详情页 | 跟踪订单全生命周期 | T019 |
| pages/delivery-prepare-progress.html | 交割准备与进度页 | 新增/详情页 | 协同交割准备和运输进度 | T020 |
| pages/delivery-accept-confirm.html | 验收提交与交割确认页 | 新增/审批页 | 提交验收并签字确认 | T021 |
| pages/delivery-exception.html | 交割异常处理页 | 审批页 | 处理交割异常和违约 | T022 |
| pages/settlement-pay-detail.html | 支付与结算详情页 | 新增/详情页 | 完成模拟支付和划转展示 | T023 |
| pages/reconciliation-invoice.html | 对账与发票管理页 | 列表/详情页 | 对账单查询导出与发票上传 | T024 |
| pages/dispute-appeal-process.html | 纠纷申诉与处理页 | 新增/审批页 | 完成纠纷提交、调解、判责 | T025 |
| pages/after-sale-credit.html | 售后服务与信用评级页 | 列表/配置页 | 管理售后和主体信用 | T026 |
| pages/screen-overview.html | 大屏总览页 | 看板页 | 展示监管态势总览 | T027 |
| pages/screen-trade.html | 交易监管页 | 看板页 | 展示交易监管指标 | T028 |
| pages/screen-source.html | 溯源监管页 | 看板页 | 展示溯源监管指标 | T029 |
| pages/warning-instruction.html | 预警中心与指令管理页 | 列表/审批页 | 形成预警-指令-反馈闭环 | T030 |
| pages/statistics-report.html | 统计报表页 | 统计分析页 | 多维统计和导出 | T031 |
| pages/message-center.html | 消息中心页 | 列表页 | 管理通知与提醒 | T032 |
| pages/integration-hub.html | 系统对接页组 | 配置/看板页 | 展示外部系统模拟对接状态 | T033 |
| pages/system-parameter-dictionary.html | 参数配置与数据字典页 | 配置页 | 管理业务参数和字典 | T034 |
| pages/system-permission.html | 权限管理页 | 配置页 | 配置角色、菜单、按钮、数据权限 | T035 |
| pages/system-log-monitor.html | 操作日志与系统监控页 | 列表/看板页 | 审计日志和运行监控 | T036 |

## 页面类型覆盖
覆盖登录、工作台、移动端、列表、详情、新增/编辑、审批处理、配置、统计报表、大屏看板、异常处理、系统对接、运维监控。

## 主要业务链路
登录 → PC工作台 → 主体审核 → 溯源录入/档案 → 挂单列表/新增 → 挂单审核 → 挂单市场/下单确认 → 订单详情 → 交割准备/验收确认 → 支付结算 → 对账发票 → 纠纷售后 → 监管大屏/预警指令。

## 限制说明
资金、支付、区块链、物联网、外部系统接口均为Mock静态演示；敏感数据已脱敏。

## 第二阶段输入来源
`系统全局功能描述与设计.md`、`系统的功能点设计.md`、`页面详细设计/`、`第二阶段设计检查报告.md`。
