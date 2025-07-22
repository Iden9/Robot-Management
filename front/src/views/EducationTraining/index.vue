<template>
  <div class="education-training">
    <div class="cards-container">
      <!-- 课件管理卡片 -->
      <SettingCard title="课件管理" :icon="DocumentIcon" iconColor="blue">
        <div class="section-title">上传教学课件</div>
        <UploadArea 
          @file-selected="handleFileSelected" 
          :loading="isUploading"
          :progress="uploadProgress"
        />
        
        <div class="section-title mt-20">大屏同步设置</div>
        <SelectField 
          label="选择模式" 
          :options="screenSyncOptions" 
          v-model="screenSyncMode" 
        />
        
        <!-- 课件操作区 -->
        <div class="courseware-actions">
          <div class="action-item">
            <ActionButton 
              text="浏览课件库" 
              type="secondary" 
              :icon="LibraryIcon"
              @click="openCoursewareLibrary"
            />
            <span class="action-desc">查看已上传的课件并进行预览</span>
          </div>
          
          <div class="action-item" v-if="selectedCourseware">
            <div class="selected-courseware">
              <div class="courseware-info">
                <span class="courseware-title">{{ selectedCourseware.title }}</span>
                <span class="courseware-type">{{ selectedCourseware.file_type.toUpperCase() }}</span>
              </div>
              <button @click="clearSelectedCourseware" class="clear-btn">✕</button>
            </div>
            <span class="action-desc">当前选择的课件</span>
          </div>
        </div>

        <div class="button-group">
          <ActionButton 
            text="开始讲课" 
            type="primary" 
            :loading="isLoading"
            @click="handleStartTeaching"
          />
          <!-- <ActionButton 
            text="高级设置" 
            type="secondary" 
            @click="handleAdvancedSettings"
          /> -->
        </div> 
      </SettingCard>
      
      <!-- AI语音设置卡片 -->
      <SettingCard title="AI语音设置" :icon="MicrophoneIcon" iconColor="blue">
        <div class="section-title">选择AI大模型平台</div>
        <SelectField 
          :options="aiPlatformOptions" 
          v-model="aiPlatform" 
        />
        
        <div class="section-title mt-20">选择科目</div>
        <SelectField 
          :options="subjectOptions" 
          v-model="selectedSubject" 
        />
        
        <div class="section-title mt-20">选择音色</div>
        <SelectField 
          :options="voiceOptions" 
          v-model="selectedVoice" 
        />
        
        <div class="section-title mt-20">机器人动作协同</div>
        <SelectField 
          :options="robotActionOptions" 
          v-model="robotAction" 
        />
        
        <div class="button-group">
          <ActionButton 
            text="测试语音" 
            type="secondary"
            @click="handleTestVoice"
          />
          <ActionButton 
            text="一键部署" 
            type="primary" 
            :loading="isLoading"
            @click="handleDeploy"
          />
        </div>
      </SettingCard>
      
      <!-- 课堂互动设置卡片 -->
      <SettingCard title="课堂互动设置" :icon="HandIcon" iconColor="blue">
        <div class="toggle-item">
          <div>
            <div class="toggle-title">举手识别功能</div>
          </div>
          <div class="toggle-with-label">
            <ToggleSwitch v-model:checked="handRecognition" />
            <span class="toggle-status">开启举手识别</span>
          </div>
        </div>
        
        <div class="toggle-item">
          <div>
            <div class="toggle-title">互动问答模式</div>
          </div>
          <div class="toggle-with-label">
            <ToggleSwitch v-model:checked="interactiveQA" />
            <span class="toggle-status">开启自动问答</span>
          </div>
        </div>
        
        <div class="section-title mt-20">导航避障设置</div>
        <SelectField 
          :options="navigationModeOptions" 
          v-model="navigationMode" 
        />
        
        <div class="button-centered">
          <ActionButton 
            text="模拟学生提问" 
            type="primary"
            @click="handleSimulateQuestion"
          />
        </div>
      </SettingCard>
    </div>

    <!-- 课件库模态框 -->
    <CoursewareLibraryModal
      :show="showLibraryModal"
      @close="closeLibraryModal"
      @select="handleCoursewareSelected"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import SettingCard from '@/components/education/SettingCard.vue'
import UploadArea from '@/components/education/UploadArea.vue'
import SelectField from '@/components/education/SelectField.vue'
import ToggleSwitch from '@/components/education/ToggleSwitch.vue'
import ActionButton from '@/components/education/ActionButton.vue'
import CoursewareLibraryModal from '@/components/education/CoursewareLibraryModal.vue'

// 图标
import DocumentIcon from '@/components/education/icons/DocumentIcon.vue'
import MicrophoneIcon from '@/components/education/icons/MicrophoneIcon.vue'
import HandIcon from '@/components/education/icons/HandIcon.vue'
import LibraryIcon from '@/components/education/icons/LibraryIcon.vue'

// Stores
import { useCoursewareStore } from '@/stores/courseware'
import { useEducationStore } from '@/stores/education'
import { success, error, confirm } from '@/utils/alert'

// 初始化stores
const coursewareStore = useCoursewareStore()
const educationStore = useEducationStore()

// 表单数据
const screenSyncMode = ref('auto')
const aiPlatform = ref('xunfei')
const selectedSubject = ref('chinese')
const selectedVoice = ref('male')
const robotAction = ref('standard')
const navigationMode = ref('default')

// 开关状态
const handRecognition = ref(true)
const interactiveQA = ref(true)

// 加载状态
const isLoading = ref(false)
const isUploading = ref(false)

// 课件库模态框状态
const showLibraryModal = ref(false)
const selectedCourseware = ref(null)

// 计算属性
const coursewareList = computed(() => coursewareStore.coursewareList)
const categories = computed(() => coursewareStore.categories)
const uploadProgress = computed(() => coursewareStore.uploadProgress)
const educationSettings = computed(() => educationStore.educationSettings)
const currentSetting = computed(() => educationStore.currentSetting)

// 选项
const screenSyncOptions = [
  { value: 'auto', label: '自动同步到大屏' },
  { value: 'manual', label: '手动同步' },
  { value: 'off', label: '不同步' }
]

const aiPlatformOptions = [
  { value: 'xunfei', label: '讯飞星火' },
  { value: 'baidu', label: '百度文心' },
  { value: 'chatgpt', label: 'ChatGPT' },
]

const subjectOptions = [
  { value: 'chinese', label: '语文' },
  { value: 'math', label: '数学' },
  { value: 'english', label: '英语' },
  { value: 'science', label: '科学' }
]

const voiceOptions = [
  { value: 'male', label: '男声 - 沉稳教师' },
  { value: 'female', label: '女声 - 温柔教师' },
  { value: 'child', label: '童声 - 活泼助手' }
]

const robotActionOptions = [
  { value: 'standard', label: '标准教学动作' },
  { value: 'active', label: '活跃互动型' },
  { value: 'calm', label: '沉稳讲解型' },
  { value: 'none', label: '无动作' }
]

const navigationModeOptions = [
  { value: 'default', label: '课堂行走模式' },
  { value: 'interactive', label: '互动巡逻模式' },
  { value: 'static', label: '静态演示模式' }
]

// 文件上传处理
const handleFileSelected = async (file) => {
  try {
    isUploading.value = true
    
    // 创建FormData对象
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', file.name.split('.')[0]) // 使用文件名作为标题
    formData.append('description', `${selectedSubject.value}课件`)
    formData.append('tags', selectedSubject.value)
    
    // 上传课件
    const result = await coursewareStore.uploadCoursewareAction(formData)
    
    if (result.success) {
      await success(`课件上传成功！\n\n文件：${file.name}\n类型：${selectedSubject.value}课件`, {
        title: '上传成功'
      })
      console.log('课件上传成功:', result.data)
    } else {
      await error(`课件上传失败：${result.message}`, {
        title: '上传失败'
      })
      console.error('课件上传失败:', result.message)
    }
  } catch (error) {
    await error(`上传课件时发生错误：${error.message}`, {
      title: '上传失败'
    })
    console.error('上传课件时发生错误:', error)
  } finally {
    isUploading.value = false
  }
}

// 开始讲课
const handleStartTeaching = async () => {
  try {
    isLoading.value = true
    
    // 构建教育设置数据
    const settingData = {
      equipment_id: 'default', // 使用默认设备，后端会自动分配第一个可用设备
      screen_sync_mode: screenSyncMode.value,
      ai_platform: aiPlatform.value,
      subject: selectedSubject.value,
      voice_type: selectedVoice.value,
      robot_action: robotAction.value,
      navigation_mode: navigationMode.value,
      hand_recognition: handRecognition.value,
      interactive_qa: interactiveQA.value
    }
    
    // 创建或更新教育设置
    const result = await educationStore.createEducationSettingAction(settingData)
    
    if (result.success) {
      console.log('开始讲课设置成功:', result.data)
      // 可以显示成功消息或跳转到讲课页面
    } else {
      console.error('开始讲课设置失败:', result.message)
    }
  } catch (error) {
    console.error('开始讲课时发生错误:', error)
  } finally {
    isLoading.value = false
  }
}

// 高级设置
/* const handleAdvancedSettings = () => {
  console.log('打开高级设置')
} */

// 测试语音
const handleTestVoice = async () => {
  try {
    // 创建测试语音设置
    const testData = {
      ai_platform: aiPlatform.value,
      voice_type: selectedVoice.value,
      subject: selectedSubject.value,
      test_text: '这是一个语音测试，请确认语音效果是否符合要求。'
    }
    
    console.log('测试语音设置:', testData)
    // 这里可以调用语音测试API
  } catch (error) {
    console.error('测试语音失败:', error)
  }
}

// 一键部署
const handleDeploy = async () => {
  try {
    isLoading.value = true
    
    // 构建部署数据
    const deployData = {
      equipment_id: 'default', // 使用默认设备，后端会自动分配第一个可用设备
      screen_sync_mode: screenSyncMode.value,
      ai_platform: aiPlatform.value,
      subject: selectedSubject.value,
      voice_type: selectedVoice.value,
      robot_action: robotAction.value,
      hand_recognition: handRecognition.value,
      interactive_qa: interactiveQA.value,
      navigation_mode: navigationMode.value
    }
    
    // 创建教育设置并部署
    const result = await educationStore.createEducationSettingAction(deployData)
    
    if (result.success) {
      console.log('一键部署成功:', result.data)
      // 可以显示成功消息
    } else {
      console.error('一键部署失败:', result.message)
    }
  } catch (error) {
    console.error('一键部署时发生错误:', error)
  } finally {
    isLoading.value = false
  }
}

// 模拟学生提问
const handleSimulateQuestion = async () => {
  try {
    // 构建模拟问答数据
    const simulateData = {
      subject: selectedSubject.value,
      interactive_qa: interactiveQA.value,
      hand_recognition: handRecognition.value,
      navigation_mode: navigationMode.value
    }
    
    console.log('模拟学生提问:', simulateData)
    // 这里可以调用模拟问答API
  } catch (error) {
    console.error('模拟学生提问失败:', error)
  }
}

// 保存当前设置
const saveCurrentSettings = async () => {
  try {
    const settingData = {
      equipment_id: 'default', // 使用默认设备，后端会自动分配
      screen_sync_mode: screenSyncMode.value,
      ai_platform: aiPlatform.value,
      subject: selectedSubject.value,
      voice_type: selectedVoice.value,
      robot_action: robotAction.value,
      navigation_mode: navigationMode.value,
      hand_recognition: handRecognition.value,
      interactive_qa: interactiveQA.value
    }
    
    const result = await educationStore.createEducationSettingAction(settingData)
    
    if (result.success) {
      console.log('设置保存成功:', result.data)
    } else {
      console.error('设置保存失败:', result.message)
    }
  } catch (error) {
    console.error('保存设置时发生错误:', error)
  }
}

// 加载课件列表
const loadCoursewareList = async () => {
  try {
    await coursewareStore.fetchCoursewareList()
    await coursewareStore.fetchCategories()
  } catch (error) {
    console.error('加载课件列表失败:', error)
  }
}

// 加载教育设置
const loadEducationSettings = async () => {
  try {
    await educationStore.fetchEducationSettings()
  } catch (error) {
    console.error('加载教育设置失败:', error)
  }
}

// 课件库相关操作
const openCoursewareLibrary = () => {
  showLibraryModal.value = true
}

const closeLibraryModal = () => {
  showLibraryModal.value = false
}

const clearSelectedCourseware = () => {
  selectedCourseware.value = null
}

const handleCoursewareSelected = async (courseware) => {
  selectedCourseware.value = courseware
  await success(`已选择课件 "${courseware.title}" 用于教学`)
  console.log('选择的课件:', courseware)
}

// 组件挂载时加载数据
onMounted(() => {
  loadEducationSettings()
})
</script>

<style scoped>
.education-training {
  width: 100%;
}

.cards-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 12px;
}

.button-group {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.mt-20 {
  margin-top: 20px;
}

.toggle-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.toggle-title {
  font-size: 14px;
  font-weight: 500;
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

.button-centered {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

/* 课件操作区样式 */
.courseware-actions {
  margin: 20px 0;
}

.action-item {
  margin-bottom: 16px;
}

.action-desc {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.selected-courseware {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #0284c7;
  border-radius: 8px;
  padding: 12px 16px;
  margin-top: 8px;
}

.courseware-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.courseware-title {
  font-weight: 500;
  color: #0f172a;
  font-size: 14px;
}

.courseware-type {
  font-size: 12px;
  color: #0284c7;
  background: rgba(2, 132, 199, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  align-self: flex-start;
}

.clear-btn {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid #fca5a5;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #dc2626;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: #dc2626;
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
</style> 