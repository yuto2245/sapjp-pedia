<template>
  <v-container class="py-8">
    <h1 class="text-h4 font-weight-bold mb-6">修正を提案</h1>

    <div v-if="loading" class="text-center">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <v-form v-else ref="form" v-model="valid" @submit.prevent="submit">
      <v-alert type="info" variant="tonal" class="mb-6">
        記事「{{ article?.title }}」への修正提案を作成します。
        管理者の承認後、記事に反映されます。
      </v-alert>

      <!-- 修正理由 -->
      <v-textarea
        v-model="proposal.reason"
        label="修正の理由（例: 情報が古い、誤字脱字、補足情報の追加）"
        :rules="[v => !!v || '修正理由は必須です']"
        variant="outlined"
        rows="3"
        class="mb-4"
      />

      <!-- 参考URL -->
      <v-text-field
        v-model="referenceUrlInput"
        label="参考URL（任意）"
        variant="outlined"
        placeholder="https://..."
        hint="Enterキーで追加"
        persistent-hint
        @keydown.enter.prevent="addReference"
      >
        <template #append-inner>
          <v-btn
            size="small"
            variant="text"
            icon="mdi-plus"
            @click="addReference"
          />
        </template>
      </v-text-field>

      <div class="mb-6">
        <v-chip
          v-for="(url, index) in proposal.reference_urls"
          :key="index"
          closable
          class="mr-2 mb-2"
          @click:close="removeReference(index)"
        >
          {{ url }}
        </v-chip>
      </div>

      <!-- 修正後の本文 -->
      <v-textarea
        v-model="proposal.after_content"
        label="修正後の本文 (Markdown)"
        :rules="[v => !!v || '本文は必須です']"
        variant="outlined"
        rows="20"
        class="mb-6 font-monospace"
      />

      <!-- アクションボタン -->
      <div class="d-flex ga-4">
        <v-btn
          color="primary"
          size="large"
          type="submit"
          :loading="submitting"
          :disabled="!valid"
        >
          提案を送信する
        </v-btn>
        <v-btn
          variant="text"
          size="large"
          @click="router.back()"
        >
          キャンセル
        </v-btn>
      </div>
    </v-form>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color">
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getArticle, proposeRevision } from '@/api'

const route = useRoute()
const router = useRouter()
const form = ref(null)
const valid = ref(false)
const loading = ref(true)
const submitting = ref(false)
const article = ref(null)
const referenceUrlInput = ref('')

const proposal = reactive({
  creator_type: 'human',
  reason: '',
  after_content: '',
  reference_urls: []
})

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success'
})

// 記事取得
const init = async () => {
  try {
    const data = await getArticle(route.params.id)
    article.value = data
    // 初期値として現在のコンテンツをセット
    proposal.after_content = data.content
  } catch (error) {
    console.error('記事取得エラー:', error)
    snackbar.text = '記事の取得に失敗しました'
    snackbar.color = 'error'
    snackbar.show = true
  } finally {
    loading.value = false
  }
}

// 参照URL追加
const addReference = () => {
  const url = referenceUrlInput.value.trim()
  if (url && !proposal.reference_urls.includes(url)) {
    proposal.reference_urls.push(url)
    referenceUrlInput.value = ''
  }
}

const removeReference = (index) => {
  proposal.reference_urls.splice(index, 1)
}

// 送信
const submit = async () => {
  if (!valid.value) return

  submitting.value = true
  try {
    await proposeRevision(route.params.id, proposal)
    
    snackbar.text = '修正提案を送信しました！管理者の承認をお待ちください。'
    snackbar.color = 'success'
    snackbar.show = true

    setTimeout(() => {
      router.push(`/articles/${route.params.id}`)
    }, 2000)
  } catch (error) {
    console.error('送信エラー:', error)
    snackbar.text = '提案の送信に失敗しました'
    snackbar.color = 'error'
    snackbar.show = true
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  init()
})
</script>

<style scoped>
.font-monospace {
  font-family: monospace;
}
</style>
