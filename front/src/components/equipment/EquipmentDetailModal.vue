<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="detail-modal" @click.stop>
      <div class="modal-header">
        <div class="header-left">
          <div class="icon-wrapper">
            <InfoIcon />
          </div>
          <h2>设备详情</h2>
        </div>
        <button @click="$emit('close')" class="close-btn">
          <CloseIcon />
        </button>
      </div>

      <div class="modal-body">
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>

        <div v-else-if="equipment" class="detail-content">
          <!-- 基本信息 -->
          <div class="info-section">
            <h3 class="section-title">基本信息</h3>
            <div class="info-grid">
              <div class="info-item">
                <label>设备ID</label>
                <span class="value device-id">{{ equipment.id }}</span>
              </div>
              <div class="info-item">
                <label>设备位置</label>
                <span class="value">{{ equipment.location || '未设置' }}</span>
              </div>
              <div class="info-item">
                <label>IP地址</label>
                <span class="value">{{ equipment.ip_address || '未分配' }}</span>
              </div>
              <div class="info-item">
                <label>状态</label>
                <span class="value">
                  <span class="status-badge" :class="getStatusClass(equipment)">
                    {{ getStatusText(equipment) }}
                  </span>
                </span>
              </div>
              <div class="info-item">
                <label>使用率</label>
                <span class="value">{{ equipment.usage_rate || '0%' }}</span>
              </div>
              <div class="info-item">
                <label>创建时间</label>
                <span class="value">{{ formatDate(equipment.created_at) }}</span>
              </div>
            </div>
          </div>

          <!-- 系统信息 -->
          <div class="info-section" v-if="equipment.system_info">
            <h3 class="section-title">系统信息</h3>
            <div class="info-grid">
              <div class="info-item">
                <label>操作系统</label>
                <span class="value">{{ equipment.system_info.os || '未知' }}</span>
              </div>
              <div class="info-item">
                <label>CPU型号</label>
                <span class="value">{{ equipment.system_info.cpu || '未知' }}</span>
              </div>
              <div class="info-item">
                <label>内存大小</label>
                <span class="value">{{ equipment.system_info.memory || '未知' }}</span>
              </div>
              <div class="info-item">
                <label>存储空间</label>
                <span class="value">{{ equipment.system_info.storage || '未知' }}</span>
              </div>
              <div class="info-item">
                <label>固件版本</label>
                <span class="value">{{ equipment.system_info.firmware_version || '未知' }}</span>
              </div>
              <div class="info-item">
                <label>软件版本</label>
                <span class="value">{{ equipment.system_info.software_version || '未知' }}</span>
              </div>
            </div>
          </div>

          <!-- 网络信息 -->
          <div class="info-section" v-if="equipment.network_info">
            <h3 class="section-title">网络信息</h3>
            <div class="info-grid">
              <div class="info-item">
                <label>MAC地址</label>
                <span class="value">{{ equipment.network_info.mac_address || '未知' }}</span>
              </div>
              <div class="info-item">
                <label>子网掩码</label>
                <span class="value">{{ equipment.network_info.subnet_mask || '未知' }}</span>
              </div>
              <div class="info-item">
                <label>网关</label>
                <span class="value">{{ equipment.network_info.gateway || '未知' }}</span>
              </div>
              <div class="info-item">
                <label>DNS服务器</label>
                <span class="value">{{ equipment.network_info.dns_server || '未知' }}</span>
              </div>
            </div>
          </div>

          <!-- 运行状态 -->
          <div class="info-section">
            <h3 class="section-title">运行状态</h3>
            <div class="info-grid">
              <div class="info-item">
                <label>运行时间</label>
                <span class="value">{{ equipment.uptime || '未知' }}</span>
              </div>
              <div class="info-item">
                <label>最后在线时间</label>
                <span class="value">{{ formatDate(equipment.last_seen) }}</span>
              </div>
              <div class="info-item">
                <label>连接状态</label>
                <span class="value">
                  <span class="connection-status" :class="equipment.is_online ? 'online' : 'offline'">
                    {{ equipment.is_online ? '在线' : '离线' }}
                  </span>
                </span>
              </div>
              <div class="info-item">
                <label>错误状态</label>
                <span class="value">
                  <span class="error-status" :class="equipment.has_error ? 'has-error' : 'no-error'">
                    {{ equipment.has_error ? '有错误' : '正常' }}
                  </span>
                </span>
              </div>
            </div>
          </div>

          <!-- 错误信息 -->
          <div class="info-section" v-if="equipment.error_message">
            <h3 class="section-title">错误信息</h3>
            <div class="error-message">
              {{ equipment.error_message }}
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <InfoIcon class="empty-icon" />
          <p>无法获取设备详情</p>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="$emit('close')" class="btn secondary">
          关闭
        </button>
        <button @click="$emit('edit', equipment)" class="btn primary">
          编辑设备
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// 图标组件
import InfoIcon from './icons/InfoIcon.vue'
import CloseIcon from './icons/CloseIcon.vue'

// Props
const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  equipment: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['close', 'edit'])

// 方法
const handleOverlayClick = () => {
  emit('close')
}

const getStatusClass = (equipment) => {
  if (equipment.has_error) return 'error'
  if (equipment.is_offline) return 'offline'
  if (equipment.status === 'online') return 'online'
  return 'unknown'
}

const getStatusText = (equipment) => {
  if (equipment.has_error) return '错误'
  if (equipment.is_offline) return '离线'
  if (equipment.status === 'online') return '在线'
  return '未知'
}

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.detail-modal {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 90vw;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  background: white;
  border-bottom: 1px solid #f0f0f0;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
}

.icon-wrapper {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0071e4;
  margin-right: 10px;
}

.modal-header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.close-btn {
  background: #f5f5f5;
  border: none;
  border-radius: 4px;
  width: 32px;
  height: 32px;
  color: #666;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #e8e8e8;
}

.close-btn svg {
  width: 16px;
  height: 16px;
}

.modal-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #999;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #0071e4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.detail-content {
  max-width: 100%;
}

.info-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item label {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

.info-item .value {
  font-size: 14px;
  color: #333;
  word-break: break-all;
}

.device-id {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.online {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.status-badge.offline {
  background: #fff2e8;
  color: #fa8c16;
  border: 1px solid #ffd591;
}

.status-badge.error {
  background: #fff2f0;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
}

.status-badge.unknown {
  background: #f5f5f5;
  color: #999;
  border: 1px solid #d9d9d9;
}

.connection-status.online {
  color: #52c41a;
  font-weight: 500;
}

.connection-status.offline {
  color: #fa8c16;
  font-weight: 500;
}

.error-status.has-error {
  color: #ff4d4f;
  font-weight: 500;
}

.error-status.no-error {
  color: #52c41a;
  font-weight: 500;
}

.error-message {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 4px;
  padding: 12px;
  color: #ff4d4f;
  font-size: 14px;
  line-height: 1.4;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #999;
}

.empty-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.modal-footer {
  border-top: 1px solid #f0f0f0;
  padding: 16px 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn.secondary {
  background: #f5f5f5;
  color: #333;
}

.btn.secondary:hover {
  background: #e8e8e8;
}

.btn.primary {
  background: #0071e4;
  color: white;
}

.btn.primary:hover {
  background: #0062c4;
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-modal {
    width: 95vw;
    max-height: 95vh;
  }
}
</style>