<template>
  <v-container class="py-12">
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        <div class="d-flex align-center mb-8">
          <h1 class="text-h4 font-weight-bold" style="font-family: 'Libre Baskerville', serif;">
            管理者ダッシュボード
          </h1>
          <v-spacer />
          <v-chip color="primary" variant="outlined" class="font-weight-bold">
            承認待ち: {{ reports.length }}件
          </v-chip>
          <v-btn icon="mdi-refresh" variant="text" @click="fetchReports" class="ml-2" />
        </div>

        <div v-if="loading" class="text-center py-12">
          <v-progress-circular indeterminate color="primary" />
        </div>

        <div v-else>
          <v-row>
            <v-col v-for="report in reports" :key="report.id" cols="12">
              <v-card class="border" style="border-color: #333 !important; background-color: #121212;">
                <v-card-text>
                  <div class="d-flex justify-space-between align-start mb-2">
                    <div class="text-h6 font-weight-bold text-white mb-1">
                      {{ report.article_title }}
                    </div>
                    <v-chip size="x-small" :color="report.creator_type === 'ai' ? 'purple-lighten-2' : 'blue-lighten-2'" variant="tonal">
                      {{ report.creator_type === 'ai' ? 'AI提案' : 'コミュニティ' }}
                    </v-chip>
                  </div>
                  
                  <div class="text-caption text-grey mb-4">
                    提案理由: <span class="text-grey-lighten-1">{{ report.reason }}</span>
                    <span class="mx-2">•</span>
                    {{ formatDate(report.created_at) }}
                  </div>

                  <div class="d-flex ga-2 justify-end">
                    <v-btn
                      variant="text"
                      color="grey"
                      size="small"
                      class="text-capitalize"
                      @click="router.push(`/articles/${report.article_id}`)"
                    >
                      記事を表示
                    </v-btn>
                    
                    <v-btn
                      color="error"
                      variant="text"
                      size="small"
                      class="text-capitalize"
                      :loading="processing === report.id"
                      @click="reject(report.id)"
                    >
                      却下
                    </v-btn>
                    
                    <v-btn
                      color="success"
                      variant="tonal"
                      size="small"
                      class="text-capitalize px-4"
                      :loading="processing === report.id"
                      @click="approve(report.id)"
                    >
                      承認して反映
                    </v-btn>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <v-alert
            v-if="reports.length === 0"
            type="success"
            variant="tonal"
            class="mt-8 border-opacity-25"
            color="grey"
          >
            承認待ちの提案はありません。すべて完了です！ 🎉
          </v-alert>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getPendingReports, approveReport, rejectReport } from '@/api'

const router = useRouter()
const reports = ref([])
const loading = ref(true)
const processing = ref(null)

// 履歴取得
const fetchReports = async () => {
  loading.value = true
  try {
    reports.value = await getPendingReports()
  } catch (error) {
    console.error('取得エラー:', error)
  } finally {
    loading.value = false
  }
}

const approve = async (id) => {
  // if (!confirm('この修正提案を承認しますか？記事が更新されます。')) return // 開発中はスキップ
  
  processing.value = id
  try {
    await approveReport(id)
    await fetchReports()
  } catch (error) {
    alert('承認に失敗しました。')
  } finally {
    processing.value = null
  }
}

const reject = async (id) => {
  if (!confirm('この修正提案を却下しますか？')) return

  processing.value = id
  try {
    await rejectReport(id)
    await fetchReports()
  } catch (error) {
    alert('却下に失敗しました。')
  } finally {
    processing.value = null
  }
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('ja-JP', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  fetchReports()
})
</script>
