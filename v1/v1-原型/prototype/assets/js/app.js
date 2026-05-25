/**
 * 智能物流管理系统 - 公共交互脚本
 */

// 侧边栏折叠
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
    }
}

// Toast 提示
function showToast(message, type = 'info') {
    // 移除已存在的 toast
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    // 触发显示动画
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    // 自动隐藏
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Modal 弹窗
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }
}

// 表单校验
function validateRequired(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('error');
            
            // 移除错误状态
            field.addEventListener('input', function() {
                this.classList.remove('error');
            }, { once: true });
        }
    });

    return isValid;
}

// 提交按钮 loading
function submitWithLoading(button, callback) {
    const originalText = button.textContent;
    button.disabled = true;
    button.classList.add('loading');
    button.textContent = '提交中...';

    setTimeout(() => {
        button.disabled = false;
        button.classList.remove('loading');
        button.textContent = originalText;
        
        if (callback) {
            callback();
        }
    }, 1000);
}

// URL 参数读取
function getUrlParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

// 筛选重置
function resetFilter(form) {
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        if (input.type === 'text' || input.tagName === 'SELECT') {
            input.value = '';
        }
    });
}

// 获取订单状态标签类
function getStatusBadgeClass(status) {
    const statusMap = {
        'pending': 'badge-warning',
        'dispatched': 'badge-info',
        'in_transit': 'badge-success',
        'arrived': 'badge-info',
        'waiting_sign': 'badge-warning',
        'completed': 'badge-success',
        'cancelled': 'badge-danger',
        'idle': 'badge-success',
        'maintenance': 'badge-warning',
        'offline': 'badge-danger',
        'on_duty': 'badge-success',
        'rest': 'badge-warning',
        'off_duty': 'badge-danger',
        'pending': 'badge-warning',
        'processing': 'badge-info',
        'handled': 'badge-success',
        'confirmed': 'badge-success'
    };
    return statusMap[status] || 'badge-info';
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 高亮当前页面对应的菜单项
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href.replace('pages/', '').replace('.html', ''))) {
            link.classList.add('active');
        }
    });

    // 为所有外部链接添加点击事件
    document.querySelectorAll('a[href$=".html"]').forEach(link => {
        link.addEventListener('click', function(e) {
            // 只处理内部页面链接
            if (this.hostname === window.location.hostname) {
                // 正常跳转，不做特殊处理
            }
        });
    });

    // 表单提交拦截
    document.querySelectorAll('form[data-validate]').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateRequired(this)) {
                e.preventDefault();
                showToast('请填写必填项', 'error');
            }
        });
    });
});

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        toggleSidebar,
        showToast,
        openModal,
        closeModal,
        validateRequired,
        submitWithLoading,
        getUrlParam,
        resetFilter,
        getStatusBadgeClass
    };
}