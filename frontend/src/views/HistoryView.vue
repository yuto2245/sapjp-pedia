<template>
  <v-container class="py-12">
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <div class="d-flex align-center mb-8">
          <v-btn
            variant="text"
            prepend-icon="mdi-arrow-left"
            @click="router.back()"
            color="grey"
            class="text-capitalize pl-0"
          >
            記事に戻る
          </v-btn>
          <v-spacer />
          <h1 class="text-h4 font-weight-bold" style="font-family: 'Libre Baskerville', serif;">
            変更履歴
          </h1>
        </div>

        <div v-if="loading" class="text-center py-12">
          <v-progress-circular indeterminate color="primary" />
        </div>

        <div v-else>
          <v-timeline side="end" align="start" density="compact" line-color="grey-darken-3">
            <v-timeline-item
              v-for="report in reports"
              :key="report.id"
              :dot-color="getDotColor(report.creator_type)"
              size="x-small"
              fill-dot
            >
              <template #opposite>
                <!-- Comapct mode hides opposite, so we rely on card content -->
              </template>

              <v-card class="elevation-0 border" style="border-color: #333 !important; background-color: #121212;">
                <v-card-text class="pt-3">
                  <div class="d-flex justify-space-between align-start mb-2">
                    <div class="text-caption text-grey">
                      {{ formatDate(report.created_at) }}
                    </div>
                    <v-chip size="x-small" :color="getDotColor(report.creator_type)" variant="outlined">
                      {{ report.creator_type === 'ai' ? 'AI自動修正' : 'コミュニティ' }}
                    </v-chip>
                  </div>
                  
                  <div class="text-body-1 font-weight-medium mb-2 text-white">
                    {{ report.reason }}
                  </div>
                </v-card-text>
                
                <v-divider style="border-color: #333;" />
                
                <v-card-actions>
                  <v-spacer />
                  <v-btn
                    variant="text"
                    color="primary"
                    size="small"
                    class="text-capitalize"
                    @click="openDiff(report.id)"
                  >
                    差分を確認
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-timeline-item>
          </v-timeline>

          <v-alert
            v-if="reports.length === 0"
            type="info"
            variant="tonal"
            class="mt-8 border-opacity-25"
            color="grey"
          >
            変更履歴はありません。
          </v-alert>
        </div>
      </v-col>
    </v-row>

    <!-- 差分表示ダイアログ -->
    <v-dialog v-model="dialog" max-width="900" scrollable>
      <v-card color="surface" class="border" style="border-color: #333 !important;">
        <v-card-title class="d-flex align-center py-4 px-6 border-b" style="border-color: #333 !important;">
          <span class="text-h6 font-weight-bold" style="font-family: 'Libre Baskerville', serif;">変更内容</span>
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" density="comfortable" @click="dialog = false" />
        </v-card-title>
        
        <v-card-text class="pa-0" style="max-height: 70vh;">
          <div v-if="diffLoading" class="text-center py-12">
            <v-progress-circular indeterminate color="primary" />
          </div>
          <div v-else class="diff-container font-monospace bg-black pa-4">
            <div
              v-for="(part, index) in diffParts"
              :key="index"
              class="diff-line"
              :class="getDiffClass(part)"
            >
              <span class="diff-marker noselect">{{ getDiffMarker(part) }}</span>
              <span class="diff-content">{{ part.value }}</span>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getArticleReports, getReport } from '@/api'
import { diffLines } from 'diff'

const route = useRoute()
const router = useRouter()
const reports = ref([])
const loading = ref(true)

// Diff用
const dialog = ref(false)
const diffLoading = ref(false)
const diffParts = ref([])

// 履歴取得
const fetchReports = async () => {
  try {
    reports.value = await getArticleReports(route.params.id)
  } catch (error) {
    console.error('履歴取得エラー:', error)
  } finally {
    loading.value = false
  }
}

// 差分表示
const openDiff = async (reportId) => {
  dialog.value = true
  diffLoading.value = true
  diffParts.value = []

  try {
    const report = await getReport(reportId)
    // 行ごとの差分を計算
    const diff = diffLines(report.before_content || '', report.after_content || '')
    diffParts.value = diff
  } catch (error) {
    alert('詳細の取得に失敗しました')
  } finally {
    diffLoading.value = false
  }
}

const getDiffClass = (part) => {
  if (part.added) return 'diff-added'
  if (part.removed) return 'diff-removed'
  return 'diff-unchanged'
}

const getDiffMarker = (part) => {
  if (part.added) return '+'
  if (part.removed) return '-'
  return ' '
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('ja-JP', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const getDotColor = (type) => {
  return type === 'ai' ? 'purple-lighten-2' : 'blue-lighten-2'
}

const getCreatorIcon = (type) => {
  return type === 'ai' ? 'mdi-robot' : 'mdi-account'
}

onMounted(() => {
  fetchReports()
})
</script>

<style scoped>
.font-monospace {
  font-family: 'Fira Code', monospace;
  font-size: 0.85rem;
  line-height: 1.5;
}

.diff-line {
  display: flex;
  white-space: pre-wrap;
}

.diff-marker {
  width: 24px;
  flex-shrink: 0;
  text-align: center;
  color: #666;
  user-select: none;
}

.diff-added {
  background-color: rgba(76, 175, 80, 0.15);
  color: #a5d6a7;
}

.diff-added .diff-marker {
  color: #a5d6a7;
}

.diff-removed {
  background-color: rgba(244, 67, 54, 0.15);
  color: #ef9a9a;
  text-decoration: none; /* 取り消し線は読みにくいので廃止 */
}

.diff-removed .diff-marker {
  color: #ef9a9a;
}

.diff-unchanged {
  color: #9e9e9e;
}
</style>
