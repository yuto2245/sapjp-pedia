<template>
  <v-container class="py-8" fluid>
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        <!-- ヘッダー -->
        <div class="d-flex align-center mb-8">
          <v-btn icon="mdi-arrow-left" variant="text" @click="router.back()" color="grey" />
          <div class="text-subtitle-2 text-grey ml-2 text-uppercase">前画面へ</div>
          <v-spacer />
          <ThemeButton 
            :loading="loading"
            @click="submit"
            :disabled="!valid"
          >
            公開する
          </ThemeButton>
        </div>

        <v-form ref="form" v-model="valid" @submit.prevent="submit">
          <!-- タイトル入力 -->
          <v-text-field
            v-model="article.title"
            placeholder="記事タイトル"
            variant="plain"
            class="title-input mb-4"
            :rules="[v => !!v || 'タイトルは必須です']"
            hide-details="auto"
          />

          <!-- メタデータ入力（1行） -->
          <div class="d-flex ga-4 mb-8">
            <v-text-field
              v-model="article.module"
              placeholder="モジュール (例: MM, SD)"
              variant="outlined"
              density="compact"
              hide-details
              style="max-width: 200px;"
              bg-color="surface"
            />
            <v-select
              v-model="article.status"
              :items="[
                { title: '下書き', value: 'draft' },
                { title: '公開', value: 'published' }
              ]"
              item-title="title"
              item-value="value"
              variant="outlined"
              density="compact"
              hide-details
              style="max-width: 150px;"
              bg-color="surface"
            />
          </div>

          <!-- エディタエリア -->
          <v-card variant="outlined" style="border-color: #333 !important; background-color: #121212;">
            <v-tabs v-model="tab" density="compact" bg-color="transparent" color="primary">
              <v-tab value="write" class="text-capitalize">編集</v-tab>
              <v-tab value="preview" class="text-capitalize">プレビュー</v-tab>
            </v-tabs>
            <v-divider style="border-color: #333;" />
            
            <v-window v-model="tab">
              <v-window-item value="write">
                <v-textarea
                  v-model="article.content"
                  placeholder="知識を共有しましょう..."
                  variant="plain"
                  rows="20"
                  class="markdown-editor pa-4"
                  hide-details
                  auto-grow
                />
              </v-window-item>
              
              <v-window-item value="preview">
                <div class="markdown-body pa-6" style="min-height: 400px;">
                  <div v-html="renderedContent" />
                </div>
              </v-window-item>
            </v-window>
          </v-card>

        </v-form>
      </v-col>
    </v-row>

    <!-- 通知 -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" location="top center">
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { createArticle } from '@/api'
import { marked } from 'marked'
import ThemeButton from '@/components/ThemeButton.vue'

const router = useRouter()
const form = ref(null)
const valid = ref(false)
const loading = ref(false)
const tab = ref('write')

const article = reactive({
  title: '',
  module: '',
  content: '',
  status: 'published'
})

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success'
})

const renderedContent = computed(() => {
  if (!article.content) return '<p class="text-grey">プレビューする内容がありません</p>'
  return marked.parse(article.content)
})

const submit = async () => {
  if (!valid.value) return

  loading.value = true
  try {
    const newArticle = await createArticle({
      ...article,
      status: 'published' // 強制公開
    })
    
    snackbar.text = '記事を公開しました！'
    snackbar.color = 'success'
    snackbar.show = true

    setTimeout(() => {
      // 作成された記事のIDを使って遷移（APIがIDを返すと仮定）
      if (newArticle && newArticle.id) {
        router.push(`/articles/${newArticle.id}`)
      } else {
        router.push('/')
      }
    }, 1500)
  } catch (error) {
    console.error('Error:', error)
    snackbar.text = '記事の公開に失敗しました。'
    snackbar.color = 'error'
    snackbar.show = true
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.title-input :deep(input) {
  font-family: 'Libre Baskerville', serif;
  font-size: 2.5rem;
  font-weight: bold;
  line-height: 1.2;
  padding: 0;
}

.markdown-editor :deep(textarea) {
  font-family: 'Fira Code', monospace;
  font-size: 0.95rem;
  line-height: 1.6;
  color: #e0e0e0;
}
</style>
