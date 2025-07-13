<template>
  <div class="self-guided-navigation">
    <div class="cards-container">
      <!-- 角色定义 -->
      <SettingCard title="角色定义" :icon="UserIcon">
        <div class="company-section">
          <div class="section-title">
            <BuildingIcon class="building-icon" />
            企业展厅
          </div>
          
          <div class="form-item">
            <div class="form-label">客户识别设置</div>
            
            <div class="recognition-group">
              <div class="recognition-item">
                <div class="recognition-label">识别到男性客户</div>
                <SelectField 
                  :options="genderVoiceOptions" 
                  v-model="maleCustomerVoice"
                  placeholder="使用女性语音"
                />
              </div>
              
              <div class="recognition-item">
                <div class="recognition-label">识别到女性客户</div>
                <SelectField 
                  :options="genderVoiceOptions" 
                  v-model="femaleCustomerVoice"
                  placeholder="使用男性语音"
                />
              </div>
              
              <div class="recognition-item">
                <div class="recognition-label">识别到小孩</div>
                <SelectField 
                  :options="childVoiceOptions" 
                  v-model="childVoice"
                  placeholder="使用卡通语音"
                />
              </div>
            </div>
          </div>
          
          <div class="form-item">
            <div class="form-label">讲解内容及时长</div>
            <TextArea 
              v-model="customContent" 
              placeholder="输入自定义讲解内容..."
              :rows="4"
            />
          </div>
          
          <div class="form-row">
            <div class="form-item half-width">
              <div class="form-label">讲解时长(分钟)</div>
              <SelectField 
                :options="durationOptions" 
                v-model="explanationDuration"
                placeholder="15"
              />
            </div>
            
            <div class="form-item half-width">
              <div class="form-label">动作协同模式</div>
              <SelectField 
                :options="cooperationModeOptions" 
                v-model="cooperationMode"
                placeholder="标准模式"
              />
            </div>
          </div>
        </div>
        
        <div class="preset-section">
          <div class="form-item">
            <div class="form-label">选择预设角色</div>
            <SelectField 
              :options="presetRoleOptions" 
              v-model="presetRole"
              placeholder="前台接待"
            />
          </div>
          
          <div class="button-centered">
            <ActionButton 
              text="保存角色配置" 
              type="primary"
              :icon="SaveIcon" 
              :loading="isSavingRole"
              @click="handleSaveRoleConfig"
            />
          </div>
        </div>
      </SettingCard>
      
      <!-- 导览基础设置 -->
      <SettingCard title="导览基础设置" :icon="SettingIcon">
        <div class="form-item">
          <div class="form-label">选择导览场景</div>
          <SelectField 
            :options="sceneOptions" 
            v-model="selectedScene" 
          />
        </div>
        
        <div class="form-item">
          <div class="form-label">选择AI大模型平台</div>
          <SelectField 
            :options="aiPlatformOptions" 
            v-model="aiPlatform" 
          />
        </div>
        
        <div class="form-item">
          <div class="form-label">选择音色</div>
          <SelectField 
            :options="voiceOptions" 
            v-model="selectedVoice" 
          />
        </div>
        
        <div class="form-item">
          <div class="form-label">场景提示词设置</div>
          <TextArea 
            v-model="scenePrompt" 
            placeholder="输入导览场景的特定提示词..."
            :rows="3"
          />
        </div>
        
        <div class="button-group">
          <ActionButton 
            text="保存配置" 
            type="secondary"
            :icon="SaveIcon" 
            :loading="isSaving"
            @click="handleSaveConfig"
          />
          <ActionButton 
            text="一键部署" 
            type="primary"
            :icon="LightningIcon" 
            :loading="isLoading"
            @click="handleDeploy"
          />
        </div>
      </SettingCard>
      
      <!-- 视觉识别设置 -->
      <SettingCard title="视觉识别设置" :icon="CameraIcon">
        <div class="toggle-item">
          <div class="toggle-title">双目摄像头功能</div>
          <div class="toggle-with-label">
            <ToggleSwitch v-model:checked="objectRecognition" />
            <span class="toggle-status">开启物品识别</span>
          </div>
        </div>
        
        <div class="form-item">
          <div class="form-label">物品识别触发动作</div>
          <SelectField 
            :options="recognitionActionOptions" 
            v-model="recognitionAction" 
          />
        </div>
        
        <div class="toggle-item">
          <div class="toggle-title">自动跟随模式</div>
          <div class="toggle-with-label">
            <ToggleSwitch v-model:checked="autoFollow" />
            <span class="toggle-status" :class="{ 'inactive': !autoFollow }">开启游客跟随</span>
          </div>
        </div>
        
        <div class="form-item">
          <div class="form-label">城管局巡检设置</div>
          <SelectField 
            :options="patrolOptions" 
            v-model="patrolMode" 
          />
        </div>
        
        <div class="button-centered">
          <ActionButton 
            text="测试识别功能" 
            type="primary"
            :icon="EyeIcon" 
            :loading="isTesting"
            @click="handleTestRecognition"
          />
        </div>
      </SettingCard>
      
      <!-- 导航与安全设置 -->
      <SettingCard title="导航与安全设置" :icon="NavigationIcon">
        <div class="form-item">
          <div class="form-label">SLAM导航模式</div>
          <SelectField 
            :options="navigationModeOptions" 
            v-model="navigationMode" 
          />
        </div>
        
        <div class="toggle-item">
          <div class="toggle-title">紧急报警功能</div>
          <div class="toggle-with-label">
            <ToggleSwitch v-model:checked="emergencyAlert" />
            <span class="toggle-status">开启110报警</span>
          </div>
        </div>
        
        <div class="form-item">
          <div class="form-label">报警设置</div>
          <SelectField 
            :options="alertOptions" 
            v-model="alertMode" 
          />
        </div>
        
        <div class="form-item">
          <div class="form-label">机器人移动速度</div>
          <Slider v-model="robotSpeed" :min="0" :max="100" />
        </div>
        
        <div class="button-centered">
          <ActionButton 
            text="开始导览" 
            type="primary"
            :icon="PlayIcon" 
            :loading="isLoading"
            @click="handleStartNavigation"
          />
        </div>
      </SettingCard>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 引入组件
import SettingCard from '@/components/navigation/SettingCard.vue'
import SelectField from '@/components/education/SelectField.vue'  // 复用教育培训的组件
import ToggleSwitch from '@/components/education/ToggleSwitch.vue'  // 复用教育培训的组件
import TextArea from '@/components/navigation/TextArea.vue'
import Slider from '@/components/navigation/Slider.vue'
import ActionButton from '@/components/education/ActionButton.vue'  // 复用教育培训的组件

// Stores
import { useNavigationStore } from '@/stores/navigation'

// 初始化stores
const navigationStore = useNavigationStore()

// 图标
import UserIcon from '@/components/navigation/icons/UserIcon.vue'
import SettingIcon from '@/components/navigation/icons/SettingIcon.vue'
import CameraIcon from '@/components/navigation/icons/CameraIcon.vue'
import NavigationIcon from '@/components/navigation/icons/NavigationIcon.vue'
import SaveIcon from '@/components/navigation/icons/SaveIcon.vue'
import LightningIcon from '@/components/navigation/icons/LightningIcon.vue'
import EyeIcon from '@/components/navigation/icons/EyeIcon.vue'
import PlayIcon from '@/components/navigation/icons/PlayIcon.vue'
import BuildingIcon from '@/components/navigation/icons/BuildingIcon.vue'

// 表单数据
const selectedScene = ref('scenic')
const aiPlatform = ref('xunfei')
const selectedVoice = ref('male')
const scenePrompt = ref('')
const recognitionAction = ref('move')
const patrolMode = ref('standard')
const navigationMode = ref('dynamic')
const alertMode = ref('auto')
const robotSpeed = ref(50)

// 角色定义相关数据
const maleCustomerVoice = ref('female')
const femaleCustomerVoice = ref('male')
const childVoice = ref('cartoon')
const customContent = ref('')
const explanationDuration = ref('15')
const cooperationMode = ref('standard')
const presetRole = ref('receptionist')

// 开关状态
const objectRecognition = ref(true)
const autoFollow = ref(false)
const emergencyAlert = ref(true)

// 加载状态
const isLoading = ref(false)
const isSaving = ref(false)
const isTesting = ref(false)
const isSavingRole = ref(false)

// 计算属性
const navigationSettings = computed(() => navigationStore.navigationSettings)
const navigationPoints = computed(() => navigationStore.navigationPoints)
const currentSetting = computed(() => navigationStore.currentSetting)
const statistics = computed(() => navigationStore.statistics)

// 下拉选项
const sceneOptions = [
  { value: 'scenic', label: '景区' },
  { value: 'museum', label: '博物馆' },
  { value: 'exhibition', label: '展览馆' },
  { value: 'company', label: '企业展厅' }
]

const aiPlatformOptions = [
  { value: 'xunfei', label: '讯飞星火' },
  { value: 'baidu', label: '百度文心' },
  { value: 'chatgpt', label: 'ChatGPT' },
]

const voiceOptions = [
  { value: 'male', label: '男声 - 专业导游' },
  { value: 'female', label: '女声 - 亲切向导' },
  { value: 'elder', label: '老者 - 历史讲解' }
]

const recognitionActionOptions = [
  { value: 'move', label: '移动到物体面前讲解' },
  { value: 'point', label: '指向并讲解' },
  { value: 'pause', label: '停止并提问' },
  { value: 'ignore', label: '不做任何动作' }
]

const patrolOptions = [
  { value: 'standard', label: '标准巡检模式' },
  { value: 'intensive', label: '密集巡检模式' },
  { value: 'simple', label: '简易巡检模式' },
  { value: 'none', label: '关闭巡检' }
]

const navigationModeOptions = [
  { value: 'dynamic', label: '动态避障模式' },
  { value: 'static', label: '静态路径模式' },
  { value: 'hybrid', label: '混合导航模式' }
]

const alertOptions = [
  { value: 'auto', label: '自动发送位置并报警' },
  { value: 'manual', label: '人工确认后报警' },
  { value: 'silent', label: '静默报警模式' }
]

// 角色定义相关选项
const genderVoiceOptions = [
  { value: 'male', label: '使用男性语音' },
  { value: 'female', label: '使用女性语音' },
  { value: 'professional', label: '使用专业语音' }
]

const childVoiceOptions = [
  { value: 'cartoon', label: '使用卡通语音' },
  { value: 'gentle', label: '使用温柔语音' },
  { value: 'playful', label: '使用活泼语音' }
]

const durationOptions = [
  { value: '5', label: '5分钟' },
  { value: '10', label: '10分钟' },
  { value: '15', label: '15分钟' },
  { value: '20', label: '20分钟' },
  { value: '30', label: '30分钟' }
]

const cooperationModeOptions = [
  { value: 'standard', label: '标准模式' },
  { value: 'interactive', label: '互动模式' },
  { value: 'presentation', label: '展示模式' },
  { value: 'guide', label: '引导模式' }
]

const presetRoleOptions = [
  { value: 'receptionist', label: '前台接待' },
  { value: 'tour_guide', label: '导游向导' },
  { value: 'sales_assistant', label: '销售助理' },
  { value: 'customer_service', label: '客服代表' },
  { value: 'exhibition_guide', label: '展厅讲解员' }
]

// 保存角色配置
const handleSaveRoleConfig = async () => {
  try {
    isSavingRole.value = true
    
    // 构建角色配置数据
    const roleConfigData = {
      male_customer_voice: maleCustomerVoice.value,
      female_customer_voice: femaleCustomerVoice.value,
      child_voice: childVoice.value,
      custom_content: customContent.value,
      explanation_duration: explanationDuration.value,
      cooperation_mode: cooperationMode.value,
      preset_role: presetRole.value
    }
    
    console.log('保存角色配置:', roleConfigData)
    
    // 这里可以调用保存角色配置的API
    // const result = await navigationStore.saveRoleConfig(roleConfigData)
    
    // 模拟保存成功
    setTimeout(() => {
      console.log('角色配置保存成功')
      isSavingRole.value = false
    }, 1000)
    
  } catch (error) {
    console.error('保存角色配置失败:', error)
    isSavingRole.value = false
  }
}

// 保存配置
const handleSaveConfig = async () => {
  try {
    isSaving.value = true
    
    // 构建导览设置数据
    const settingData = {
      equipment_id: 'default', // 使用默认设备，后端会自动分配
      scene: selectedScene.value,
      ai_platform: aiPlatform.value,
      voice_type: selectedVoice.value,
      scene_prompt: scenePrompt.value,
      object_recognition: objectRecognition.value,
      recognition_action: recognitionAction.value,
      auto_follow: autoFollow.value,
      patrol_mode: patrolMode.value,
      navigation_mode: navigationMode.value,
      emergency_alert: emergencyAlert.value,
      alert_mode: alertMode.value,
      robot_speed: robotSpeed.value
    }
    
    // 创建导览设置
    const result = await navigationStore.createNavigationSettingAction(settingData)
    
    if (result.success) {
      console.log('导览配置保存成功:', result.data)
      // 可以显示成功消息
    } else {
      console.error('导览配置保存失败:', result.message)
    }
  } catch (error) {
    console.error('保存导览配置时发生错误:', error)
  } finally {
    isSaving.value = false
  }
}

// 一键部署
const handleDeploy = async () => {
  try {
    isLoading.value = true
    
    // 先保存配置
    await handleSaveConfig()
    
    // 构建部署数据
    const deployData = {
      scene: selectedScene.value,
      ai_platform: aiPlatform.value,
      voice_type: selectedVoice.value,
      scene_prompt: scenePrompt.value,
      object_recognition: objectRecognition.value,
      recognition_action: recognitionAction.value,
      auto_follow: autoFollow.value,
      patrol_mode: patrolMode.value,
      navigation_mode: navigationMode.value,
      emergency_alert: emergencyAlert.value,
      alert_mode: alertMode.value,
      robot_speed: robotSpeed.value
    }
    
    console.log('一键部署导览设置:', deployData)
    // 这里可以调用部署API
    
  } catch (error) {
    console.error('一键部署失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 测试识别功能
const handleTestRecognition = async () => {
  try {
    isTesting.value = true
    
    // 构建测试数据
    const testData = {
      object_recognition: objectRecognition.value,
      recognition_action: recognitionAction.value,
      auto_follow: autoFollow.value
    }
    
    console.log('测试视觉识别功能:', testData)
    // 这里可以调用测试识别API
    
    // 模拟测试结果
    setTimeout(() => {
      console.log('识别功能测试完成')
      isTesting.value = false
    }, 2000)
    
  } catch (error) {
    console.error('测试识别功能失败:', error)
    isTesting.value = false
  }
}

// 开始导览
const handleStartNavigation = async () => {
  try {
    isLoading.value = true
    
    // 构建导览启动数据
    const navigationData = {
      scene: selectedScene.value,
      ai_platform: aiPlatform.value,
      voice_type: selectedVoice.value,
      scene_prompt: scenePrompt.value,
      navigation_mode: navigationMode.value,
      emergency_alert: emergencyAlert.value,
      alert_mode: alertMode.value,
      robot_speed: robotSpeed.value,
      object_recognition: objectRecognition.value,
      auto_follow: autoFollow.value,
      patrol_mode: patrolMode.value
    }
    
    console.log('开始导览:', navigationData)
    // 这里可以调用开始导览API
    
  } catch (error) {
    console.error('开始导览失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 更新当前设置
const updateCurrentSettings = async (settingId) => {
  try {
    const result = await navigationStore.fetchNavigationSettingDetail(settingId)
    
    if (result.success && result.data) {
      const setting = result.data
      // 更新表单数据
      selectedScene.value = setting.scene || 'scenic'
      aiPlatform.value = setting.ai_platform || 'xunfei'
      selectedVoice.value = setting.voice_type || 'male'
      scenePrompt.value = setting.scene_prompt || ''
      objectRecognition.value = setting.object_recognition !== false
      recognitionAction.value = setting.recognition_action || 'move'
      autoFollow.value = setting.auto_follow || false
      patrolMode.value = setting.patrol_mode || 'standard'
      navigationMode.value = setting.navigation_mode || 'dynamic'
      emergencyAlert.value = setting.emergency_alert !== false
      alertMode.value = setting.alert_mode || 'auto'
      robotSpeed.value = setting.robot_speed || 50
    }
  } catch (error) {
    console.error('更新设置失败:', error)
  }
}

// 加载导览设置列表
const loadNavigationSettings = async () => {
  try {
    await navigationStore.fetchNavigationSettings()
    await navigationStore.fetchNavigationPoints()
  } catch (error) {
    console.error('加载导览设置失败:', error)
  }
}

// 加载导览统计
const loadNavigationStatistics = async () => {
  try {
    await navigationStore.fetchNavigationStatistics()
  } catch (error) {
    console.error('加载导览统计失败:', error)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadNavigationSettings()
  loadNavigationStatistics()
})
</script>

<style scoped>
.self-guided-navigation {
  width: 100%;
}

.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.form-item {
  margin-bottom: 20px;
}

.form-label {
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
}

.toggle-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toggle-title {
  font-size: 14px;
  color: #333;
}

.toggle-with-label {
  display: flex;
  align-items: center;
}

.toggle-status {
  margin-left: 8px;
  font-size: 14px;
  color: #52c41a;
}

.toggle-status.inactive {
  color: #bfbfbf;
}

.button-group {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.button-centered {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

@media (max-width: 1200px) {
  .cards-container {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .cards-container {
    grid-template-columns: 1fr;
  }
}

/* 角色定义样式 */
.company-section {
  border-left: 3px solid #17a2b8;
  padding-left: 16px;
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #17a2b8;
  margin-bottom: 16px;
}

.building-icon {
  margin-right: 8px;
  width: 18px;
  height: 18px;
  color: #17a2b8;
}

.recognition-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recognition-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.recognition-label {
  font-size: 14px;
  color: #333;
  min-width: 120px;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-item.half-width {
  flex: 1;
}

.preset-section {
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
  margin-top: 20px;
}
</style> 