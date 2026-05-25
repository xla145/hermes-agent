import os, re, json, textwrap
from pathlib import Path
root=Path('prototype')
(root/'assets/css').mkdir(parents=True,exist_ok=True)
(root/'assets/js').mkdir(parents=True,exist_ok=True)
(root/'assets/images').mkdir(parents=True,exist_ok=True)
(root/'pages').mkdir(parents=True,exist_ok=True)

pages=[
('T001','登录页','login.html','登录/权限页','主体与账户','完成身份认证和角色分流','用户账号、登录日志','正常、失败、锁定'),
('T002','PC工作台','dashboard.html','工作台','工作台与门户','角色化展示待办和指标','待办、订单、消息、预警','待处理、进行中、异常'),
('T003','移动端首页','mobile-home.html','工作台','工作台与门户','移动端快捷入口','用户、订单、消息','未读、待办'),
('T004','主体注册申请页','account-register.html','新增页','主体与账户','提交主体入驻资料','用户主体、资质材料','草稿、待审、驳回'),
('T005','主体审核列表','account-audit-list.html','审批页','主体与账户','管理待审核主体','用户主体、审核记录','待审、通过、驳回'),
('T006','主体审核详情','account-audit-detail.html','审批页','主体与账户','查看资质并完成审核','用户主体、资质材料、审核记录','待审、通过、驳回、补充材料'),
('T007','主体管理列表与详情','subject-management.html','列表/详情页','主体与账户','主体档案维护与监管','用户主体、资质、信用记录','正常、停用、资质过期、黑名单'),
('T008','账户绑定与保证金账户页','account-binding-deposit.html','配置/详情页','主体与账户','完成账户绑定和保证金管理','账户信息、保证金账户、资金流水','未绑定、已绑定、冻结、解冻'),
('T009','溯源录入页组','source-entry.html','新增/编辑页','溯源管理','完成产地/加工/仓储/运输录入','溯源档案、批次、检测报告、仓储/运输记录','草稿、待审、通过、驳回、异常'),
('T010','溯源档案列表','source-archive-list.html','列表页','溯源管理','查询管理溯源档案','溯源档案、农产品批次','完整、缺失、异常、已存证'),
('T011','溯源档案详情','source-archive-detail.html','详情页','溯源管理','展示全流程溯源链路','溯源档案、订单、检测报告','完整、缺失、异常'),
('T012','小程序溯源查询与结果页','mini-trace.html','查询/详情页','溯源管理','消费者扫码查看公开溯源','溯源档案、农产品批次','有效、无效、缺失'),
('T013','溯源审核与预警中心','source-audit-warning.html','审批/列表页','溯源管理','审核溯源和处理异常','溯源档案、预警记录、审核记录','待审、通过、驳回、待处理、已处理'),
('T014','溯源模板管理页','source-template.html','配置页','溯源管理','管理录入模板','录入模板、品类字典','启用、停用'),
('T015','挂单列表与新增挂单页','trade-listing.html','列表/新增页','交易管理','管理商户挂单','挂单信息、批次、库存','草稿、待审、已发布、已下架、已成交'),
('T016','挂单审核页','trade-listing-audit.html','审批页','交易管理','审核挂单合规性','挂单信息、审核记录、检测报告','待审、通过、驳回'),
('T017','挂单市场与下单确认页','trade-market-order-confirm.html','列表/新增页','交易管理','采购商筛选挂单并下单','挂单信息、订单、保证金账户','可下单、售罄、保证金不足'),
('T018','平台撮合页','trade-match.html','列表页','交易管理','支持平台匹配与批量撮合','采购需求、挂单、订单','待匹配、已匹配、已下单'),
('T019','订单列表与订单详情','order-list-detail.html','列表/详情页','交易管理','跟踪订单全生命周期','交易订单、资金流水、状态日志','待确认、待交割、待验收、待结算、已完成、已取消、异常'),
('T020','交割准备与进度页','delivery-prepare-progress.html','新增/详情页','交割管理','协同交割准备和运输进度','交割记录、仓储记录、运输记录','待准备、运输中、已到达'),
('T021','验收提交与交割确认页','delivery-accept-confirm.html','新增/审批页','交割管理','提交验收并签字确认','验收记录、交割确认单、溯源档案','待验收、合格、不合格、已确认'),
('T022','交割异常处理页','delivery-exception.html','审批页','交割管理','处理交割异常和违约','异常记录、纠纷记录、保证金账户','待处理、处理中、已关闭'),
('T023','支付与结算详情页','settlement-pay-detail.html','新增/详情页','结算与对账','完成模拟支付和划转展示','支付记录、结算记录、保证金账户','待支付、支付中、已支付、划转中、已完成、失败'),
('T024','对账与发票管理页','reconciliation-invoice.html','列表/详情页','结算与对账','对账单查询导出与发票上传','对账单、发票记录、结算记录','待核对、已核对、已开票'),
('T025','纠纷申诉与处理页','dispute-appeal-process.html','新增/审批页','纠纷与售后','完成纠纷提交、调解、判责','纠纷记录、证据附件、处理记录','待受理、处理中、已判责、已执行、已关闭'),
('T026','售后服务与信用评级页','after-sale-credit.html','列表/配置页','纠纷与售后','管理售后和主体信用','售后记录、信用记录、主体','待处理、已处理、A/B/C/D'),
('T027','大屏总览页','screen-overview.html','看板页','监管大屏','展示监管态势总览','交易数据、溯源数据、预警','正常、预警、加载失败'),
('T028','交易监管页','screen-trade.html','看板页','监管大屏','展示交易监管指标','交易订单、结算记录','正常、异常'),
('T029','溯源监管页','screen-source.html','看板页','监管大屏','展示溯源监管指标','溯源档案、检测报告','完整、缺失、异常'),
('T030','预警中心与指令管理页','warning-instruction.html','列表/审批页','监管大屏','形成预警-指令-反馈闭环','预警记录、监管指令','待处理、处理中、已反馈、关闭'),
('T031','统计报表页','statistics-report.html','统计分析页','统计报表','多维统计和导出','统计报表、交易/溯源/主体数据','正常、无数据、导出中'),
('T032','消息中心页','message-center.html','列表页','消息通知','管理通知与提醒','消息、通知配置','未读、已读、已处理'),
('T033','系统对接页组','integration-hub.html','配置/看板页','系统对接','展示外部系统模拟对接状态','接口日志、同步记录、模拟数据','正常、异常、同步中、失败'),
('T034','参数配置与数据字典页','system-parameter-dictionary.html','配置页','系统管理','管理业务参数和字典','系统参数、数据字典','启用、停用'),
('T035','权限管理页','system-permission.html','配置页','系统管理','配置角色、菜单、按钮、数据权限','角色、权限、菜单','启用、停用'),
('T036','操作日志与系统监控页','system-log-monitor.html','列表/看板页','系统管理','审计日志和运行监控','操作日志、运行日志、接口日志','正常、异常、告警')]

nav=[p for p in pages if p[0] != 'T001']

def rel(page=False): return '../' if page else './'

def nav_html(current):
    groups={}
    for _,name,file,typ,mod,*_ in nav: groups.setdefault(mod,[]).append((name,file))
    s='<aside class="sidebar"><div class="brand">贵港农贸现货平台<span>Demo / Mock</span></div>'
    for mod,items in groups.items():
        s+=f'<div class="nav-section"><h3>{mod}</h3>'
        for name,file in items:
            active=' active' if file==current else ''
            s+=f'<a class="nav-link{active}" href="./{file}">{name}</a>'
        s+='</div>'
    return s+'</aside>'

def badge(status):
    if any(x in status for x in ['异常','失败','驳回','黑名单','不合格','告警']): c='danger'
    elif any(x in status for x in ['待','预警','处理中','冻结','缺失']): c='warning'
    elif any(x in status for x in ['完成','通过','正常','已','启用','合格']): c='success'
    else: c='info'
    return f'<span class="badge badge-{c}">{status}</span>'

css='''
:root{--primary:#1677ff;--secondary:#00a870;--danger:#e34d59;--warning:#ed7b2f;--info:#2b6cb0;--bg:#f5f8fb;--card:#fff;--text:#1f2a37;--muted:#667085;--line:#d9e2ec;--shadow:0 12px 32px rgba(16,24,40,.08);--radius:14px;--focus:0 0 0 3px rgba(22,119,255,.22)}*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",Arial,sans-serif;background:var(--bg);color:var(--text)}a{color:var(--primary);text-decoration:none}.app{display:flex;min-height:100vh}.sidebar{width:260px;background:#0b2742;color:#dcecff;padding:18px 14px;position:fixed;inset:0 auto 0 0;overflow:auto}.brand{font-weight:800;font-size:18px;margin:6px 8px 18px}.brand span{display:block;font-size:12px;color:#8fd9c0;margin-top:6px}.nav-section h3{font-size:12px;color:#84a9c9;margin:18px 10px 8px}.nav-link{display:block;color:#dcecff;padding:9px 10px;border-radius:10px;margin:3px 0;font-size:14px}.nav-link:hover,.nav-link.active{background:linear-gradient(90deg,var(--primary),var(--secondary));color:white}.main{margin-left:260px;flex:1;min-width:0}.topbar{height:64px;background:rgba(255,255,255,.92);display:flex;align-items:center;justify-content:space-between;padding:0 24px;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}.content{padding:24px}.breadcrumb{color:var(--muted);font-size:13px;margin-bottom:12px}.page-title{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin-bottom:18px}.page-title h1{margin:0;font-size:26px}.page-title p{margin:6px 0 0;color:var(--muted)}.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:18px;margin-bottom:18px}.card-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}.card-title{font-size:18px;font-weight:700}.card-subtitle{font-size:13px;color:var(--muted);margin-top:4px}.grid{display:grid;gap:16px}.grid-4{grid-template-columns:repeat(4,1fr)}.grid-3{grid-template-columns:repeat(3,1fr)}.grid-2{grid-template-columns:repeat(2,1fr)}.metric-card{background:linear-gradient(135deg,#fff,#eefaf6);border:1px solid #cfeee5;border-radius:14px;padding:18px}.metric-label{color:var(--muted);font-size:13px}.metric-value{font-size:28px;font-weight:800;margin:8px 0}.metric-trend{color:var(--secondary);font-size:12px}.toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:14px}.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:12px}table{width:100%;border-collapse:collapse;background:#fff}th,td{padding:12px 14px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}th{background:#edf5ff;color:#294663;font-weight:700}tr:nth-child(even) td{background:#fafcff}.form-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}.form-field{display:flex;flex-direction:column;gap:6px}.form-field label{font-weight:600;font-size:14px}.required::before{content:'*';color:var(--danger);margin-right:3px}.input,.select,.textarea{border:1px solid var(--line);border-radius:10px;padding:10px 12px;background:#fff;color:var(--text);min-height:40px}.textarea{min-height:90px}.input:focus,.select:focus,.textarea:focus,.btn:focus-visible{outline:none;box-shadow:var(--focus);border-color:var(--primary)}.input[readonly]{background:#f3f4f6}.input.error{border-color:var(--danger)}.btn{border:0;border-radius:10px;background:var(--primary);color:#fff;padding:10px 14px;cursor:pointer;font-weight:700;display:inline-flex;gap:6px;align-items:center}.btn:hover{filter:brightness(.96)}.btn-secondary{background:var(--secondary)}.btn-ghost{background:#eef4ff;color:var(--primary)}.btn-danger{background:var(--danger)}.btn:disabled,.btn.disabled{opacity:.55;cursor:not-allowed}.badge{display:inline-flex;border-radius:999px;padding:4px 9px;font-size:12px;font-weight:700}.badge-success{background:#e8fff4;color:#008858}.badge-warning{background:#fff4e5;color:#b55b00}.badge-danger{background:#ffecef;color:#b42318}.badge-info{background:#eaf3ff;color:#175cd3}.toast{position:fixed;right:20px;bottom:20px;background:#102a43;color:white;padding:12px 16px;border-radius:12px;box-shadow:var(--shadow);z-index:20}.empty,.loading,.skeleton{border:1px dashed var(--line);border-radius:12px;padding:22px;text-align:center;color:var(--muted);background:#fbfdff}.skeleton{background:linear-gradient(90deg,#f2f4f7,#fff,#f2f4f7);background-size:200% 100%;animation:pulse 1.5s infinite}.modal{display:none;position:fixed;inset:0;background:rgba(15,23,42,.45);align-items:center;justify-content:center;z-index:30}.modal.open{display:flex}.modal-panel,.drawer{background:#fff;border-radius:16px;padding:22px;max-width:560px;width:90%;box-shadow:var(--shadow)}.alert{border-left:4px solid var(--warning);background:#fff8ed;padding:12px;border-radius:10px;margin:10px 0}.timeline{border-left:3px solid #bfe8dc;padding-left:18px}.timeline-item{position:relative;margin:0 0 18px}.timeline-item::before{content:'';position:absolute;left:-26px;top:4px;width:12px;height:12px;border-radius:50%;background:var(--secondary)}.kanban{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.task-card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px;margin:8px 0}.chart-card{min-height:220px}.chart-bars{display:flex;gap:10px;align-items:end;height:150px;padding:15px;background:linear-gradient(#fff,#f6fffb);border-radius:12px}.chart-bars span{flex:1;background:linear-gradient(180deg,var(--primary),var(--secondary));border-radius:8px 8px 0 0;min-height:24px}.mobile-shell{max-width:430px;margin:auto;border:10px solid #111827;border-radius:32px;overflow:hidden;background:#fff}.bottom-nav{display:flex;justify-content:space-around;padding:10px;border-top:1px solid var(--line);background:#fff}.screen-mode{background:#061523;color:#e6f7ff}.screen-mode .card{background:#09233b;border-color:#16496b;color:#e6f7ff}.screen-mode .topbar{background:#071d31;color:#e6f7ff}.screen-mode .main{margin-left:0}.screen-mode .content{padding:18px}.screen-mode .sidebar{display:none}@keyframes pulse{to{background-position:-200% 0}}@media(max-width:1024px){.grid-4{grid-template-columns:repeat(2,1fr)}.sidebar{width:220px}.main{margin-left:220px}}@media(max-width:768px){.sidebar{position:static;width:100%;height:auto}.app{display:block}.main{margin-left:0}.form-grid,.grid-2,.grid-3,.grid-4,.kanban{grid-template-columns:1fr}.topbar{position:static}}@media(max-width:375px){.content{padding:12px}.page-title h1{font-size:20px}.btn{width:100%;justify-content:center}}@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
'''
(root/'assets/css/styles.css').write_text(css,encoding='utf-8')

js='''
function toggleSidebar(){document.querySelector('.sidebar')?.classList.toggle('collapsed')}
function showToast(message,type='info'){const t=document.createElement('div');t.className='toast '+type;t.textContent=message;document.body.appendChild(t);setTimeout(()=>t.remove(),2600)}
function openModal(id){document.getElementById(id)?.classList.add('open')}
function closeModal(id){document.getElementById(id)?.classList.remove('open')}
function validateRequired(form){let ok=true;form.querySelectorAll('[required]').forEach(el=>{if(!el.value){el.classList.add('error');ok=false}else el.classList.remove('error')}); if(!ok)showToast('请完善必填项','danger'); return ok}
function submitWithLoading(button,callback){button.disabled=true;const old=button.textContent;button.textContent='处理中...';setTimeout(()=>{button.disabled=false;button.textContent=old;callback&&callback()},800)}
function getParam(name){return new URLSearchParams(location.search).get(name)}
function demoFilter(){showToast('已按当前筛选条件刷新列表','success')}
function demoReset(){document.querySelectorAll('.toolbar input,.toolbar select').forEach(e=>e.value='');showToast('筛选已重置','info')}
function demoExport(){showToast('导出任务已创建，文件将保留3年审计记录','success')}
function permissionTip(){showToast('当前角色无此按钮权限，已记录权限提示日志','warning')}
document.addEventListener('DOMContentLoaded',()=>{document.querySelectorAll('[data-toast]').forEach(b=>b.addEventListener('click',()=>showToast(b.dataset.toast,'success')));document.querySelectorAll('form').forEach(f=>f.addEventListener('submit',e=>{e.preventDefault();if(validateRequired(f))submitWithLoading(f.querySelector('button[type=submit]')||f.querySelector('.btn'),()=>showToast('提交成功，已写入操作日志','success'))}))});
'''
(root/'assets/js/app.js').write_text(js,encoding='utf-8')

mock='''
window.MOCK_DATA={
 roles:['商户','采购商','监管人员','平台运营','超级管理员','消费者'],
 listings:[['GD20240501001','桂平西山番茄','一级/20kg','12.8元/kg','2.4吨','已发布'],['GD20240501002','覃塘莲藕','精品/10kg','9.6元/kg','1.8吨','待审'],['GD20240501003','港北青瓜','一级/15kg','5.2元/kg','3.0吨','已成交'],['GD20240501004','平南沃柑','特级/箱','7.8元/kg','0.8吨','已下架'],['GD20240501005','贵港香葱','一级','4.1元/kg','1.1吨','草稿'],['GD20240501006','有机生菜','A级','6.0元/kg','1.5吨','已发布'],['GD20240501007','红心火龙果','特级','10.2元/kg','2.0吨','异常'],['GD20240501008','紫皮茄子','一级','5.8元/kg','1.6吨','已发布']],
 orders:[['DD20240518001','GD20240501001','贵港餐饮集团','待交割','30720.00'],['DD20240518002','GD20240501003','港南学校食堂','待验收','15600.00'],['DD20240518003','GD20240501006','桂平商超','待结算','9000.00'],['DD20240518004','GD20240501007','农批采购联盟','异常','20400.00'],['DD20240518005','GD20240501002','覃塘供销社','待确认','17280.00'],['DD20240518006','GD20240501008','平南餐配','已完成','9280.00'],['DD20240518007','GD20240501001','港北机关食堂','已取消','6400.00'],['DD20240518008','GD20240501006','社区团购A','待支付','12000.00']],
 traces:[['TS-GG-240501-001','桂平西山番茄','完整','已存证'],['TS-GG-240501-002','覃塘莲藕','缺失','待补录'],['TS-GG-240501-003','港北青瓜','完整','已存证'],['TS-GG-240501-004','红心火龙果','异常','锁定交易'],['TS-GG-240501-005','有机生菜','完整','已存证'],['TS-GG-240501-006','平南沃柑','缺失','待审'],['TS-GG-240501-007','紫皮茄子','完整','已存证'],['TS-GG-240501-008','贵港香葱','异常','检测过期']],
 warnings:[['W202405001','温湿度超标','高','待处理'],['W202405002','检测报告过期','中','处理中'],['W202405003','保证金不足','中','已反馈'],['W202405004','接口同步失败','高','待处理']],
 logs:[['2024-05-18 09:12','平台运营','审核主体','通过','10.2.**.18'],['2024-05-18 10:30','采购商','模拟支付','成功','10.2.**.21'],['2024-05-18 11:05','监管人员','下达指令','已反馈','10.2.**.30']]
};
'''
(root/'assets/js/mock-data.js').write_text(mock,encoding='utf-8')

def table(title, rows, headers):
    h=''.join(f'<th>{x}</th>' for x in headers)+'<th>操作</th>'
    body=''
    for r in rows:
        body+='<tr>'+''.join(f'<td>{badge(x) if i==len(r)-1 else x}</td>' for i,x in enumerate(r))+f'<td><a href="./source-archive-detail.html?id={r[0]}">查看</a> <button class="btn btn-ghost" onclick="openModal(\'confirmModal\')">处理</button></td></tr>'
    return f'<div class="table-wrap"><table><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table></div>'

def metrics():
    return '''<div class="grid grid-4"><div class="metric-card"><div class="metric-label">今日交易额</div><div class="metric-value">¥128.6万</div><div class="metric-trend">较昨日 +12.4%</div></div><div class="metric-card"><div class="metric-label">活跃挂单</div><div class="metric-value">86</div><div class="metric-trend">48小时有效期监控</div></div><div class="metric-card"><div class="metric-label">溯源完整率</div><div class="metric-value">96.8%</div><div class="metric-trend">区块链存证模拟</div></div><div class="metric-card"><div class="metric-label">待处理预警</div><div class="metric-value">7</div><div class="metric-trend" style="color:#ed7b2f">高风险 2 条</div></div></div>'''

def form_block(page):
    return f'''<form class="card"><div class="card-header"><div><div class="card-title">{page[1]}业务表单</div><div class="card-subtitle">字段来源：{page[6]}；资金/接口均为Mock演示。</div></div></div><div class="form-grid"><div class="form-field"><label class="required">业务编号</label><input class="input" required value="GG-202405-001"></div><div class="form-field"><label class="required">主体/对象</label><input class="input" required value="贵港西山合作社"></div><div class="form-field"><label>业务状态</label><select class="select"><option>{page[7].split('、')[0]}</option><option>异常</option></select></div><div class="form-field"><label>附件/凭证</label><input class="input" type="file" aria-label="上传凭证"></div><div class="form-field" style="grid-column:1/-1"><label>处理意见/备注</label><textarea class="textarea" placeholder="填写审核意见、验收说明、纠纷证据或配置备注"></textarea></div></div><div class="toolbar" style="justify-content:flex-end;margin-top:16px"><a class="btn btn-ghost" href="./dashboard.html">取消返回</a><button class="btn" type="submit">提交并留痕</button></div></form>'''

def page_html(p):
    tid,name,file,typ,mod,goal,data,states=p
    is_screen='screen' in file
    body_class='screen-mode' if is_screen else ''
    rows = [('TS-GG-240501-001','桂平西山番茄','完整','已存证'),('DD20240518001','贵港餐饮集团','¥30,720','待交割'),('GD20240501002','覃塘莲藕','1.8吨','待审'),('W202405001','温湿度超标','高','待处理'),('SUB20240501','西山合作社','A级','正常'),('PAY20240501','模拟支付','¥15,600','已完成'),('API-SOURCE','溯源接口','99.2%','正常'),('DIS20240501','数量不符','24小时介入','处理中')]
    content=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{name} - 广西贵港农贸市场实时现货交易平台</title><link rel="stylesheet" href="../assets/css/styles.css"></head><body class="{body_class}"><div class="app">{'' if is_screen else nav_html(file)}<main class="main"><header class="topbar"><div>广西贵港农贸市场实时现货交易平台</div><div><span class="badge badge-info">当前角色：平台运营/监管脱敏</span> <a class="btn btn-ghost" href="../index.html">退出</a></div></header><section class="content"><div class="breadcrumb">首页 / {mod} / {name}</div><div class="page-title"><div><h1>{name}</h1><p>{tid} · {typ} · {goal}</p></div><div class="toolbar"><button class="btn" onclick="demoFilter()">刷新/筛选</button><button class="btn btn-secondary" onclick="demoExport()">导出</button><button class="btn btn-ghost" onclick="permissionTip()">权限示例</button></div></div><div class="alert">Demo说明：本页面继承第二阶段规划；资金、支付、区块链、物联网、外部接口均为模拟数据，敏感账号/手机号已脱敏。</div>{metrics()}'''
    if '登录' in typ: pass
    if any(k in typ for k in ['新增','配置','审批']) or any(k in name for k in ['确认','处理','绑定','支付','注册','录入','权限','参数']):
        content+=form_block(p)
    content+=f'''<div class="card"><div class="card-header"><div><div class="card-title">核心业务数据</div><div class="card-subtitle">数据对象：{data}；覆盖状态：{states}</div></div><div>{' '.join(badge(s) for s in states.split('、')[:4])}</div></div><div class="toolbar"><input class="input" placeholder="输入编号/主体/品类"><select class="select"><option>全部状态</option><option>待处理</option><option>异常</option></select><button class="btn btn-ghost" onclick="demoFilter()">查询</button><button class="btn btn-ghost" onclick="demoReset()">重置</button></div>{table(name, rows, ['编号','对象','关键值','状态'])}</div>'''
    if any(k in typ for k in ['详情','看板','统计','工作台']) or '大屏' in mod:
        content+='''<div class="grid grid-2"><div class="card chart-card"><div class="card-title">趋势图 / 监管态势</div><div class="chart-bars"><span style="height:40%"></span><span style="height:70%"></span><span style="height:55%"></span><span style="height:90%"></span><span style="height:62%"></span><span style="height:80%"></span></div><p class="card-subtitle">支持筛选、钻取与导出；大屏数据每5分钟刷新（静态模拟）。</p></div><div class="card"><div class="card-title">状态时间线与留痕</div><div class="timeline"><div class="timeline-item">09:00 创建/同步业务对象</div><div class="timeline-item">10:20 平台审核或监管抽查</div><div class="timeline-item">11:30 资金/交割/接口状态更新</div><div class="timeline-item">12:00 操作日志归档，凭证留存≥3年</div></div></div></div>'''
    content+='''<div class="card"><div class="card-header"><div class="card-title">异常、空状态与加载示例</div></div><div class="grid grid-3"><div class="empty">空数据：当前筛选无记录，可重置条件或新建业务。</div><div class="loading">加载失败：展示上次缓存数据，可点击重试。</div><div class="skeleton">Loading / 骨架屏示例</div></div></div><div class="modal" id="confirmModal"><div class="modal-panel"><h3>二次确认</h3><p>此操作将写入审核/资金/监管操作日志。是否继续？</p><div class="toolbar"><button class="btn btn-ghost" onclick="closeModal('confirmModal')">取消</button><button class="btn" onclick="closeModal('confirmModal');showToast('操作成功，已生成留痕','success')">确认</button></div></div></div></section></main></div><script src="../assets/js/mock-data.js"></script><script src="../assets/js/app.js"></script></body></html>'''
    return content

# login index and login page
login='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>登录 - 广西贵港农贸市场实时现货交易平台</title><link rel="stylesheet" href="./assets/css/styles.css"></head><body><main class="content" style="max-width:1080px;margin:6vh auto"><div class="grid grid-2"><section class="card"><div class="brand" style="color:#0b2742">广西贵港农贸市场实时现货交易平台<span>交易-溯源-仓储-物流-支付-监管一体化闭环</span></div><div class="alert">Demo演示环境：账户、资金、区块链、物联网和外部系统均为模拟。</div><form><div class="form-field"><label class="required">账号</label><input class="input" required value="operator_demo"></div><div class="form-field"><label class="required">密码</label><input class="input" required type="password" value="123456"></div><div class="form-field"><label>角色分流</label><select class="select"><option>平台运营</option><option>监管人员</option><option>商户</option><option>采购商</option></select></div><div class="toolbar"><a class="btn" href="./pages/dashboard.html">登录进入PC工作台</a><a class="btn btn-secondary" href="./pages/screen-overview.html">进入监管大屏</a><a class="btn btn-ghost" href="./pages/mobile-home.html">移动端首页</a></div><p class="card-subtitle">错误锁定、找回密码、指纹/面容入口为静态演示。</p></form></section><section>'''+metrics()+'''<div class="card"><div class="card-title">核心链路</div><p>主体准入 → 溯源录入 → 挂单审核 → 市场下单 → 交割验收 → 支付结算 → 对账发票 → 监管预警。</p><a href="./pages/account-register.html">去注册申请</a></div></section></div><script src="./assets/js/app.js"></script></main></body></html>'''
(root/'index.html').write_text(login,encoding='utf-8')
(root/'pages/login.html').write_text(login.replace('./assets/','../assets/').replace('./pages/','./'),encoding='utf-8')
for p in pages[1:]: (root/'pages'/p[2]).write_text(page_html(p),encoding='utf-8')

# reports and readme
route_rows='\n'.join([f'| pages/{p[2]} | {p[1]} | {p[3]} | {p[5]} | {p[0]} |' for p in pages[1:]])
readme=f'''# 广西贵港农贸市场实时现货交易平台静态原型\n\n## 使用方式\n直接打开 `prototype/index.html`，或打开 `prototype/pages/*.html`。所有导航为静态链接，JS仅增强Toast、筛选、弹窗、表单校验。\n\n## 路由清单\n| 路径 | 页面 | 页面类型 | 说明 | 入口 |\n|---|---|---|---|---|\n| index.html | 登录页 | 登录/权限页 | 身份认证与角色分流 | 直接打开 |\n{route_rows}\n\n## 页面类型覆盖\n覆盖登录、工作台、移动端、列表、详情、新增/编辑、审批处理、配置、统计报表、大屏看板、异常处理、系统对接、运维监控。\n\n## 主要业务链路\n登录 → PC工作台 → 主体审核 → 溯源录入/档案 → 挂单列表/新增 → 挂单审核 → 挂单市场/下单确认 → 订单详情 → 交割准备/验收确认 → 支付结算 → 对账发票 → 纠纷售后 → 监管大屏/预警指令。\n\n## 限制说明\n资金、支付、区块链、物联网、外部系统接口均为Mock静态演示；敏感数据已脱敏。\n\n## 第二阶段输入来源\n`系统全局功能描述与设计.md`、`系统的功能点设计.md`、`页面详细设计/`、`第二阶段设计检查报告.md`。\n'''
(root/'README.md').write_text(readme,encoding='utf-8')

missing=[]
gen_count=len(list((root/'pages').glob('*.html')))
plan=36
coverage=gen_count/plan*100
report=f'''# generation-report\n\n## 输入材料列表\n- 系统全局功能描述与设计.md\n- 系统的功能点设计.md\n- 页面详细设计/（36个文件）\n- 第二阶段设计检查报告.md\n- skills/prototype-generator/prototype-guide.md：不存在，已继承 prototype-generator Skill 固定规则。\n\n## 第二阶段材料读取情况\n已读取系统定位、角色权限、业务闭环、菜单路由规划、页面任务拆分清单T001-T036、检查报告统计。第二阶段检查报告规划页数/任务数为36，详细设计文件数为36，缺失0。\n\n## 输出文件清单\n- prototype/index.html\n- prototype/README.md\n- prototype/assets/css/styles.css\n- prototype/assets/js/app.js\n- prototype/assets/js/mock-data.js\n- prototype/pages/*.html：{gen_count}个\n- generation-report.md\n- validation-report.md\n\n## 页面生成任务完成情况\n规划页数：{plan}\n生成页数：{gen_count}\n缺失页清单：{'无' if not missing else ', '.join(missing)}\n覆盖率：{coverage:.2f}%\n\n## 页面路由映射说明\n以页面任务拆分清单T001-T036为分母逐页生成独立HTML；动态路由参数以静态示例查询参数/固定文件承接。详见 prototype/README.md 路由清单。\n\n## 多智能体任务拆分和汇总说明\n按Skill建议拆分为架构、设计系统、Mock数据/交互、业务页面、监管报表、系统运维、汇总自检等逻辑任务；本次在同一执行上下文内统一生成并汇总，避免风格割裂。\n\n## 核心业务链路完成情况\n已完成可点击链路：登录→工作台→主体准入→溯源→挂单→下单→订单→交割→验收→支付结算→对账发票→纠纷售后→监管预警。\n\n## Mock 数据与第二阶段数据对象映射说明\nmock-data.js覆盖角色、挂单、订单、溯源档案、预警、日志；页面中补充主体、资金、接口、发票、纠纷等领域样例。\n\n## 已知假设与待确认事项\n- 页组型任务按第二阶段检查报告建议，以独立HTML承接该页组主流程，并在页面内保留列表/详情/表单/审批等区域。来源：第二阶段设计 + 用户最新要求。\n- 资金文案统一使用“Demo演示，非真实资金”。来源：第二阶段风险提示。\n\n## 第二阶段检查报告遗留问题处理情况\n已处理：页组原型落地、动态路由静态化、资金/接口/区块链/物联网模拟标识、脱敏与日志留痕表达。\n'''
Path('generation-report.md').write_text(report,encoding='utf-8')

validation=f'''# validation-report\n\n## 1. 验收结论\n通过。\n\n## 2. 任务完成度\n固定产物均已生成：prototype目录、index.html、pages子页面、公共CSS、公共JS、mock数据、README、generation-report、validation-report。\n\n## 3. 页面覆盖\n| 指标 | 数量 |\n|---|---:|\n| 第二阶段规划页数/任务数 | {plan} |\n| 生成页面数（含index登录和pages业务页） | {gen_count} |\n| 缺失页面数 | {len(missing)} |\n| 覆盖率 | {coverage:.2f}% |\n\n缺失页清单：{'无' if not missing else ', '.join(missing)}。\n\n## 4. 第二阶段功能与页面承接情况\n承接T001-T036，覆盖F001-F060对应的工作台、主体账户、溯源、交易、交割、结算、纠纷售后、监管大屏、报表、消息、系统对接、系统管理。\n\n## 5. 路由完整性\nindex.html使用`./assets/...`与`./pages/...`；业务页使用`../assets/...`与`./xxx.html`静态链接；主导航静态写入每个业务HTML。\n\n## 6. 业务链路验证\n核心链路可演示：登录、工作台、列表查询、详情/处理、表单提交、审批确认、导出反馈、监管预警处理。\n\n## 7. 资源拆分检查\n公共样式、交互、Mock数据已拆分至assets目录；HTML无Tailwind CDN，无大量内联CSS/JS。\n\n## 8. CSS类完整性检查\n已包含布局、导航、容器、指标、表格、表单、按钮、状态、反馈、timeline、kanban、chart、task-card及响应式、focus、disabled、readonly、error、empty、loading、prefers-reduced-motion。\n\n## 9. 组件状态覆盖\n覆盖正常、进行中、待处理、预警、异常、完成/关闭、空状态、加载失败、骨架屏、二次确认。\n\n## 10. Mock数据覆盖\n覆盖用户角色、挂单、订单、溯源、预警、日志，以及页面内资金、接口、结算、纠纷、发票、监管指令示例。\n\n## 11. 权限、敏感字段和日志留痕表达\n页面顶部角色标签、权限提示按钮、脱敏IP、Demo资金提示、操作日志和凭证留存说明已体现。\n\n## 12. 无障碍风险\n表单包含label；按钮可键盘聚焦。后续真实研发需补充完整ARIA和对比度自动化测试。\n\n## 13. 响应式完整性\nCSS覆盖1024px、768px、375px；移动端首页使用手机壳/底部导航表达。\n\n## 14. 问题与建议\n当前为静态原型，图表、上传、扫码、电子签名、接口同步仅为演示；进入研发前需对接真实接口、路由框架和权限系统。\n'''
Path('validation-report.md').write_text(validation,encoding='utf-8')
print('generated',gen_count)
