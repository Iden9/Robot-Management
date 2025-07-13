// 简单的loading指令实现
export const vLoading = {
  mounted(el, binding) {
    if (binding.value) {
      addLoading(el)
    }
  },
  updated(el, binding) {
    if (binding.value !== binding.oldValue) {
      if (binding.value) {
        addLoading(el)
      } else {
        removeLoading(el)
      }
    }
  },
  unmounted(el) {
    removeLoading(el)
  }
}

function addLoading(el) {
  const loadingEl = document.createElement('div')
  loadingEl.className = 'loading-overlay'
  loadingEl.innerHTML = `
    <div class="loading-spinner">
      <div class="spinner"></div>
      <div class="loading-text">加载中...</div>
    </div>
  `
  
  // 添加样式
  loadingEl.style.cssText = `
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
  `
  
  const spinnerEl = loadingEl.querySelector('.loading-spinner')
  spinnerEl.style.cssText = `
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
  `
  
  const spinnerDotEl = loadingEl.querySelector('.spinner')
  spinnerDotEl.style.cssText = `
    width: 32px;
    height: 32px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #0071e4;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  `
  
  const textEl = loadingEl.querySelector('.loading-text')
  textEl.style.cssText = `
    color: #666;
    font-size: 14px;
  `
  
  // 添加动画样式
  if (!document.querySelector('#loading-keyframes')) {
    const style = document.createElement('style')
    style.id = 'loading-keyframes'
    style.textContent = `
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    `
    document.head.appendChild(style)
  }
  
  // 确保父元素有relative定位
  if (getComputedStyle(el).position === 'static') {
    el.style.position = 'relative'
  }
  
  el.appendChild(loadingEl)
  el.setAttribute('data-loading', 'true')
}

function removeLoading(el) {
  const loadingEl = el.querySelector('.loading-overlay')
  if (loadingEl) {
    el.removeChild(loadingEl)
  }
  el.removeAttribute('data-loading')
}

export default vLoading