<template>
  <div class="system-settings">
    <div class="settings-grid">
      <!-- 服务器设置 -->
      <SettingCard title="服务器设置" :icon="ServerIcon" iconColor="blue">
        <div class="setting-group">
          <div class="setting-row">
            <div class="setting-label">服务器地址</div>
            <div class="setting-control">
              <input type="text" v-model="serverSettings.address" class="input-field" placeholder="请输入服务器地址" />
            </div>
          </div>
          
          <div class="setting-row">
            <div class="setting-label">端口号</div>
            <div class="setting-control">
              <input type="number" v-model="serverSettings.port" class="input-field" placeholder="请输入端口号" />
            </div>
          </div>
          
          <div class="setting-row">
            <div class="setting-label">连接超时（秒）</div>
            <div class="setting-control">
              <input type="number" v-model="serverSettings.timeout" class="input-field" placeholder="请输入超时时间" />
            </div>
          </div>
          
          <div class="setting-row">
            <div class="setting-label">自动重连</div>
            <div class="setting-control toggle-container">
              <ToggleSwitch v-model:checked="serverSettings.autoReconnect" />
              <span class="toggle-label">{{ serverSettings.autoReconnect ? '开启' : '关闭' }}</span>
            </div>
          </div>
        </div>
        
        <div class="action-buttons">
          <ActionButton text="测试连接" :loading="isTesting" @click="testConnection" />
          <ActionButton text="保存设置" :icon="SaveIcon" primary :loading="isSaving" @click="saveServerSettings" />
        </div>
      </SettingCard>
      
      <!-- 通知设置 -->
      <SettingCard title="通知设置" :icon="BellIcon" iconColor="orange">
        <div class="setting-group">
          <div class="setting-row">
            <div class="setting-label">设备离线通知</div>
            <div class="setting-control toggle-container">
              <ToggleSwitch v-model:checked="notificationSettings.deviceOffline" />
              <span class="toggle-label">{{ notificationSettings.deviceOffline ? '开启' : '关闭' }}</span>
            </div>
          </div>
          
          <div class="setting-row">
            <div class="setting-label">设备错误通知</div>
            <div class="setting-control toggle-container">
              <ToggleSwitch v-model:checked="notificationSettings.deviceError" />
              <span class="toggle-label">{{ notificationSettings.deviceError ? '开启' : '关闭' }}</span>
            </div>
          </div>
          
          <div class="setting-row">
            <div class="setting-label">系统更新通知</div>
            <div class="setting-control toggle-container">
              <ToggleSwitch v-model:checked="notificationSettings.systemUpdate" />
              <span class="toggle-label">{{ notificationSettings.systemUpdate ? '开启' : '关闭' }}</span>
            </div>
          </div>
          
          <div class="setting-row">
            <div class="setting-label">通知方式</div>
            <div class="setting-control">
              <div class="checkbox-group">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="notificationSettings.methods.email" />
                  <span>邮件</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" v-model="notificationSettings.methods.sms" />
                  <span>短信</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" v-model="notificationSettings.methods.push" />
                  <span>推送</span>
                </label>
              </div>
            </div>
          </div>
        </div>
        
        <div class="action-buttons">
          <ActionButton text="保存设置" :icon="SaveIcon" primary :loading="isSaving" @click="saveNotificationSettings" />
        </div>
      </SettingCard>
      
      <!-- 安全设置 -->
      <SettingCard title="安全设置" :icon="LockIcon" iconColor="red">
        <div class="setting-group">
          <div class="setting-row">
            <div class="setting-label">密码复杂度要求</div>
            <div class="setting-control">
              <select v-model="securitySettings.passwordComplexity" class="select-field">
                <option value="low">低 (仅字母或数字)</option>
                <option value="medium">中 (字母+数字)</option>
                <option value="high">高 (字母+数字+特殊字符)</option>
              </select>
            </div>
          </div>
          
          <div class="setting-row">
            <div class="setting-label">密码有效期（天）</div>
            <div class="setting-control">
              <input type="number" v-model="securitySettings.passwordExpiry" class="input-field" placeholder="0表示永不过期" />
            </div>
          </div>
          
          <div class="setting-row">
            <div class="setting-label">登录失败锁定</div>
            <div class="setting-control toggle-container">
              <ToggleSwitch v-model:checked="securitySettings.loginLockEnabled" />
              <span class="toggle-label">{{ securitySettings.loginLockEnabled ? '开启' : '关闭' }}</span>
            </div>
          </div>
          
          <div class="setting-row" v-if="securitySettings.loginLockEnabled">
            <div class="setting-label">失败尝试次数</div>
            <div class="setting-control">
              <input type="number" v-model="securitySettings.loginLockAttempts" class="input-field" placeholder="请输入失败尝试次数" />
            </div>
          </div>
        </div>
        
        <div class="action-buttons">
          <ActionButton text="保存设置" :icon="SaveIcon" primary :loading="isSaving" @click="saveSecuritySettings" />
        </div>
      </SettingCard>
      
      <!-- 数据管理 -->
      <SettingCard title="数据管理" :icon="DatabaseIcon" iconColor="purple">
        <div class="setting-group">
          <div class="setting-row">
            <div class="setting-label">数据备份频率</div>
            <div class="setting-control">
              <select v-model="dataSettings.backupFrequency" class="select-field">
                <option value="daily">每日</option>
                <option value="weekly">每周</option>
                <option value="monthly">每月</option>
              </select>
            </div>
          </div>
          
          <div class="setting-row">
            <div class="setting-label">保留备份数量</div>
            <div class="setting-control">
              <input type="number" v-model="dataSettings.backupRetention" class="input-field" placeholder="请输入保留数量" />
            </div>
          </div>
          
          <div class="setting-row">
            <div class="setting-label">自动清理日志</div>
            <div class="setting-control toggle-container">
              <ToggleSwitch v-model:checked="dataSettings.autoCleanLogs" />
              <span class="toggle-label">{{ dataSettings.autoCleanLogs ? '开启' : '关闭' }}</span>
            </div>
          </div>
          
          <div class="setting-row" v-if="dataSettings.autoCleanLogs">
            <div class="setting-label">日志保留天数</div>
            <div class="setting-control">
              <input type="number" v-model="dataSettings.logRetentionDays" class="input-field" placeholder="请输入保留天数" />
            </div>
          </div>
        </div>
        
        <div class="action-buttons">
          <ActionButton text="立即备份" :loading="isBackuping" @click="backupNow" />
          <ActionButton text="保存设置" :icon="SaveIcon" primary :loading="isSaving" @click="saveDataSettings" />
        </div>
      </SettingCard>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import SettingCard from '@/components/settings/SettingCard.vue'
import ToggleSwitch from '@/components/settings/ToggleSwitch.vue'
import ActionButton from '@/components/settings/ActionButton.vue'

// 图标
import ServerIcon from '@/components/settings/icons/ServerIcon.vue'
import BellIcon from '@/components/settings/icons/BellIcon.vue'
import LockIcon from '@/components/settings/icons/LockIcon.vue'
import DatabaseIcon from '@/components/settings/icons/DatabaseIcon.vue'
import SaveIcon from '@/components/settings/icons/SaveIcon.vue'

// 导入alert工具函数
import { success, error } from '@/utils/alert'

// Stores
import { useSystemStore } from '@/stores/system'

// 初始化stores
const systemStore = useSystemStore()

// 加载状态
const isLoading = ref(false)
const isTesting = ref(false)
const isSaving = ref(false)

// 计算属性
const systemConfig = computed(() => systemStore.systemConfig)
const systemInfo = computed(() => systemStore.systemInfo)
const backupList = computed(() => systemStore.backupList)
const isBackuping = computed(() => systemStore.isBackuping)

// 服务器设置
const serverSettings = ref({
  address: '192.168.1.100',
  port: 8080,
  timeout: 30,
  autoReconnect: true
})

// 通知设置
const notificationSettings = ref({
  deviceOffline: true,
  deviceError: true,
  systemUpdate: false,
  methods: {
    email: true,
    sms: false,
    push: true
  }
})

// 安全设置
const securitySettings = ref({
  passwordComplexity: 'medium',
  passwordExpiry: 90,
  loginLockEnabled: true,
  loginLockAttempts: 5
})

// 数据管理
const dataSettings = ref({
  backupFrequency: 'daily',
  backupRetention: 7,
  autoCleanLogs: true,
  logRetentionDays: 30
})

// 处理函数
const testConnection = async () => {
  try {
    isTesting.value = true
    
    // 模拟连接测试
    console.log('测试连接', serverSettings.value)
    
    // 这里可以调用实际的连接测试API
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    console.log('连接测试成功')
  } catch (error) {
    console.error('连接测试失败:', error)
  } finally {
    isTesting.value = false
  }
}

const saveServerSettings = async () => {
  try {
    isSaving.value = true
    
    // 构建配置数据
    const configData = {
      server: {
        address: serverSettings.value.address,
        port: serverSettings.value.port,
        timeout: serverSettings.value.timeout,
        auto_reconnect: serverSettings.value.autoReconnect
      }
    }
    
    // 更新系统配置
    const result = await systemStore.updateSystemConfigAction(configData)
    
    if (result.success) {
      success(result.message || '服务器设置保存成功')
      console.log('服务器设置保存成功')
    } else {
      error(result.message || '服务器设置保存失败')
      console.error('服务器设置保存失败:', result.message)
    }
  } catch (error) {
    error('保存服务器设置失败: ' + (error.message || ''))
    console.error('保存服务器设置失败:', error)
  } finally {
    isSaving.value = false
  }
}

const saveNotificationSettings = async () => {
  try {
    isSaving.value = true
    
    // 构建配置数据
    const configData = {
      notification: {
        device_offline: notificationSettings.value.deviceOffline,
        device_error: notificationSettings.value.deviceError,
        system_update: notificationSettings.value.systemUpdate,
        methods: {
          email: notificationSettings.value.methods.email,
          sms: notificationSettings.value.methods.sms,
          push: notificationSettings.value.methods.push
        }
      }
    }
    
    // 更新系统配置
    const result = await systemStore.updateSystemConfigAction(configData)
    
    if (result.success) {
      success(result.message || '通知设置保存成功')
      console.log('通知设置保存成功')
    } else {
      error(result.message || '通知设置保存失败')
      console.error('通知设置保存失败:', result.message)
    }
  } catch (err) {
    error('保存通知设置失败: ' + (err.message || ''))
    console.error('保存通知设置失败:', err)
  } finally {
    isSaving.value = false
  }
}

const saveSecuritySettings = async () => {
  try {
    isSaving.value = true
    
    // 构建配置数据
    const configData = {
      security: {
        password_complexity: securitySettings.value.passwordComplexity,
        password_expiry: securitySettings.value.passwordExpiry,
        login_lock_enabled: securitySettings.value.loginLockEnabled,
        login_lock_attempts: securitySettings.value.loginLockAttempts
      }
    }
    
    // 更新系统配置
    const result = await systemStore.updateSystemConfigAction(configData)
    
    if (result.success) {
      success(result.message || '安全设置保存成功')
      console.log('安全设置保存成功')
    } else {
      error(result.message || '安全设置保存失败')
      console.error('安全设置保存失败:', result.message)
    }
  } catch (err) {
    error('保存安全设置失败: ' + (err.message || ''))
    console.error('保存安全设置失败:', err)
  } finally {
    isSaving.value = false
  }
}

const saveDataSettings = async () => {
  try {
    isSaving.value = true
    
    // 构建配置数据
    const configData = {
      data: {
        backup_frequency: dataSettings.value.backupFrequency,
        backup_retention: dataSettings.value.backupRetention,
        auto_clean_logs: dataSettings.value.autoCleanLogs,
        log_retention_days: dataSettings.value.logRetentionDays
      }
    }
    
    // 更新系统配置
    const result = await systemStore.updateSystemConfigAction(configData)
    
    if (result.success) {
      success(result.message || '数据设置保存成功')
      console.log('数据设置保存成功')
    } else {
      error(result.message || '数据设置保存失败')
      console.error('数据设置保存失败:', result.message)
    }
  } catch (err) {
    error('保存数据设置失败: ' + (err.message || ''))
    console.error('保存数据设置失败:', err)
  } finally {
    isSaving.value = false
  }
}

const backupNow = async () => {
  try {
    // 构建备份数据
    const backupData = {
      type: 'manual',
      description: '手动立即备份',
      include_logs: true,
      include_config: true,
      include_data: true
    }
    
    // 创建系统备份
    const result = await systemStore.createSystemBackupAction(backupData)
    
    if (result.success) {
      success(result.message || '立即备份启动成功')
      console.log('立即备份启动成功:', result.data)
    } else {
      error(result.message || '立即备份失败')
      console.error('立即备份失败:', result.message)
    }
  } catch (err) {
    error('立即备份失败: ' + (err.message || ''))
    console.error('立即备份失败:', err)
  }
}

// 加载系统配置
const loadSystemConfig = async () => {
  try {
    isLoading.value = true
    const result = await systemStore.fetchSystemConfig()
    
    if (result.success && result.data) {
      const config = result.data
      
      // 更新本地设置
      if (config.server) {
        serverSettings.value = {
          address: config.server.address || '192.168.1.100',
          port: config.server.port || 8080,
          timeout: config.server.timeout || 30,
          autoReconnect: config.server.auto_reconnect !== false
        }
      }
      
      if (config.notification) {
        notificationSettings.value = {
          deviceOffline: config.notification.device_offline !== false,
          deviceError: config.notification.device_error !== false,
          systemUpdate: config.notification.system_update || false,
          methods: {
            email: config.notification.methods?.email !== false,
            sms: config.notification.methods?.sms || false,
            push: config.notification.methods?.push !== false
          }
        }
      }
      
      if (config.security) {
        securitySettings.value = {
          passwordComplexity: config.security.password_complexity || 'medium',
          passwordExpiry: config.security.password_expiry || 90,
          loginLockEnabled: config.security.login_lock_enabled !== false,
          loginLockAttempts: config.security.login_lock_attempts || 5
        }
      }
      
      if (config.data) {
        dataSettings.value = {
          backupFrequency: config.data.backup_frequency || 'daily',
          backupRetention: config.data.backup_retention || 7,
          autoCleanLogs: config.data.auto_clean_logs !== false,
          logRetentionDays: config.data.log_retention_days || 30
        }
      }
    }
  } catch (error) {
    console.error('加载系统配置失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 加载系统信息和备份列表
const loadSystemData = async () => {
  try {
    await Promise.all([
      systemStore.fetchSystemInfo(),
      systemStore.fetchBackupList()
    ])
  } catch (error) {
    console.error('加载系统数据失败:', error)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadSystemConfig()
  loadSystemData()
})
</script>

<style scoped>
/* .system-settings {
  padding: 20px;
} */

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.setting-group {
  /* margin-bottom: 20px; */
}

.setting-row {
  display: flex;
  margin-bottom: 16px;
  align-items: center;
}

.setting-label {
  width: 140px;
  font-size: 14px;
  color: #333;
}

.setting-control {
  flex: 1;
}

.input-field, .select-field {
  width: 100%;
  height: 36px;
  padding: 0 12px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.input-field:focus, .select-field:focus {
  outline: none;
  border-color: #0071e4;
  box-shadow: 0 0 0 2px rgba(0, 113, 228, 0.1);
}

.toggle-container {
  display: flex;
  align-items: center;
}

.toggle-label {
  margin-left: 8px;
  font-size: 14px;
  color: #666;
}

.checkbox-group {
  display: flex;
  gap: 16px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-label input {
  margin-right: 4px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

@media (max-width: 1200px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .setting-row {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .setting-label {
    width: 100%;
    margin-bottom: 8px;
  }
}
</style> 