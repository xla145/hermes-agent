
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
