<template>
  <v-container class="fill-height">
    <v-row justify="center" align="center" class="flex-column" style="min-height: 60vh;">
      <!-- アスキーアート (ブロック) -->
      <v-col cols="12" class="text-center mb-n8 position-relative" style="z-index: 1;">
        <pre class="ascii-art font-weight-bold">
██████████████████████████████████████████████▓▓████████████████████████▓▓████████████████████████████████████████████████
████████████████████████████████████████████████████████▓▓████████████████████████████████████████████████████████████████
██████████████████████████████▓▓██████████████████████████████████████████████████████████████████████████████████████████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
████████████████████████▓▓██████████████████████████▓▓██████████████████████████████████████████████████████████████▓▓████
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
████████████████████████████████████████████████████████████████████████████████████████▓▓████████████████████████████████
████████████████████████████▓▓██████████████████████████▓▓████████████████████████████████████████▓▓██████████████████████
██████████████████▒▒░░▒▒████████████████████████████████████████████▓▓████████████▓▓██████████████████████████████████████
████████████████▒▒░░    ██████████████████████████████▓▓██████████████████████████████████████████████████████████████████
██▓▓████████████░░░░▓▓████████████████████████████████████████████████████████████████████████████████████████████████████
████████████████░░▒▒████████████████████████████████████████████▓▓████████████████████████████████████████████████████████
████████████████░░▒▒██████████████████████████████████████████████████████████████████████████████████████████████████████
██████▓▓████████░░░░▓▓██████████████████████████████████████████████▓▓████████████████████████████▒▒██████▒▒██████████████
████████████████▓▓░░░░████████████████████████████████████████████████████████████████████████████████████████████████████
██████████████████▒▒░░▓▓████▓▓██████████████████████████████████████████████████████████████████████▓▓██████▓▓████████████
████████████████████░░░░████████████████████████████████████████████████▓▓██▓▓████████▓▓████▓▓▓▓▓▓██▓▓██████▒▒████████████
████████████████████▓▓░░▒▒██████████████████████████████▓▓▓▓████████████████▓▓▓▓▓▓████▓▓██▓▓▓▓▓▓▓▓▒▒▓▓████▓▓██████████████
██████████████████████▒▒░░██████████████████████████▓▓██▒▒▒▒▓▓▓▓▓▓▓▓▓▓██▓▓▓▓▒▒▓▓▓▓██████████▓▓▓▓██████▓▓████▒▒████████████
████████████████████████░░░░██████████████████████████▓▓▒▒▒▒▒▒░░░░▒▒▓▓▓▓▓▓▓▓░░██▓▓██▓▓▓▓▓▓██████████▓▓▓▓██████████████████
██████████████████████████░░▒▒██▒▒██████████████████▓▓▒▒▒▒▒▒▒▒▒▒░░▒▒▒▒▒▒░░▒▒▓▓████████▓▓████▓▓▓▓▓▓██▓▓▒▒▒▒▓▓▓▓▓▓██████████
████▓▓██████████████▓▓██████░░▓▓████████████████▓▓▓▓░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░▓▓▓▓██████████▓▓██▓▓▓▓▓▓▓▓████████████████████
████████████████████████████▓▓░░▓▓██▓▓████████▓▓▓▓▒▒▒▒▒▒░░░░░░░░░░░░▒▒░░▒▒▒▒▓▓▓▓▓▓▓▓██████████▓▓░░▓▓▓▓▓▓██▓▓██████████████
██████████████████████████████▒▒░░██████████▓▓▓▓░░▒▒░░░░░░░░░░░░░░▒▒▒▒▒▒░░▒▒▒▒██▓▓████████████▒▒██▓▓▓▓  ▓▓████████████████
████████████████████████████████▓▓░░████████▓▓░░░░░░░░░░░░░░░░░░░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓████▓▓▓▓▓▓▓▓▓▓░░  ██████████████████
▒▒████████████████████████████████▒▒░░██████▓▓    ░░░░░░    ░░░░▒▒▒▒▒▒▒▒▒▒░░▒▒▒▒  ▓▓████████▒▒▓▓▓▓▓▓▓▓████████████████████
████████████████████████████████████▒▒░░▓▓▓▓▓▓░░  ░░░░        ░░░░░░░░░░░░░░░░▒▒░░▓▓████████████▓▓▓▓██████████████████████
██████████▓▓██████████████▓▓████▓▓▓▓▓▓▓▓░░▒▒▓▓░░  ░░░░      ░░░░░░▒▒▒▒▒▒░░  ░░░░  ▓▓██████▓▓██▓▓██████████████████████████
████████████████████████████████▒▒▓▓▓▓▓▓▓▓▒▒░░    ▒▒▒▒░░░░░░░░▒▒▒▒▒▒░░░░  ░░░░░░  ▒▒▒▒▓▓▓▓▓▓██████████████████████████████
████████████████▓▓██████████████▓▓▒▒▓▓░░██▓▓▓▓░░░░    ░░  ░░░░░░▒▒▒▒░░░░  ░░░░░░▒▒▓▓▓▓▒▒▓▓▓▓░░██████████████████████▓▓████
████████████████████████████████▓▓▒▒████████░░▒▒░░░░▒▒░░      ▒▒▒▒▒▒▒▒░░      ▓▓▓▓▓▓▒▒████████████████████████████████████
████████████████████████▓▓▓▓▓▓▓▓▓▓████▓▓████░░    ░░░░░░▒▒    ░░░░░░░░░░░░      ▒▒▓▓████████▓▓████████████████████████████
████▓▓████████████████████▒▒▓▓▓▓▓▓██████████▒▒    ░░░░          ░░░░░░▓▓██▓▓          ████████▓▓████████████████████████▓▓
██████████████████████▓▓▓▓▓▓▓▓██████▓▓▓▓▓▓████▒▒░░  ░░░░    ░░░░  ░░░░▓▓▓▓░░    ░░    ▓▓██████████████████████████████████
████████████████████▓▓▓▓▓▓▓▓▓▓████████████████▒▒▓▓▓▓░░░░░░░░░░░░░░░░░░░░▒▒    ░░░░  ░░████████████████████████████████████
▓▓████████████████▓▓▓▓▓▓▓▓▓▓▓▓██████████████████▓▓▓▓▓▓    ▒▒▓▓░░  ░░░░      ▓▓▒▒▒▒░░██████████████████████████████████████
████████████████▓▓▓▓▓▓▓▓▓▓████████▒▒████████████▓▓▓▓▓▓▓▓░░▓▓▒▒▒▒          ▓▓▓▓██████████████████████▓▓████████████████████
████████████████████░░  ██▓▓▓▓▓▓▓▓████▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒░░    ▓▓▒▒██▓▓▓▓██████████████████████████████████████████
▓▓██████▒▒████████▓▓░░▓▓▓▓▒▒▓▓██▒▒▓▓▒▒▓▓████▓▓██▓▓▓▓▒▒▓▓▓▓▓▓▓▓▓▓▒▒▒▒░░▒▒▒▒▓▓██████████████████████████████████████████████
██▓▓██████████████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██████████████▓▓▓▓▓▓████████▒▒▓▓██████████████████▓▓░░████████████████████████████
██████████████████████░░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓▓██████████████████████████▓▓▒▒▓▓████████████████████████▓▓████████████████████
██████████████████▓▓▓▓██▓▓▓▓▓▓▓▓██▓▓▓▓████████████████████████████████████▒▒▓▓▓▓████████████████▓▓▓▓████▓▓▓▓██████████████
████████████████████████████████████████████████████████████████████████████▓▓▒▒▓▓████████████████████████████████████████
██████████▓▓▓▓██████████████████████████████████████████████████████████████░░▓▓▓▓▒▒████████████▓▓██▓▓████████████████████
██████████████████████▒▒▓▓██████████████████████████▓▓██████████████████▓▓████████████▓▓▒▒▓▓██▓▓██████████████████▓▓▓▓████
██████████████████████▓▓██████████████████████████▓▓▒▒▓▓██████████████████▓▓██████▓▓▓▓▒▒▓▓▓▓██▓▓▓▓████████▓▓▓▓▓▓██████████
██████████████████████▓▓▓▓████████████████████████████████████████████████▓▓██████████▓▓▒▒▒▒██▓▓██████████████████▓▓▓▓████
██▓▓████████████████████████████████████▓▓████████████▓▓▓▓████▓▓▓▓▓▓██████▓▓▓▓▓▓████████▓▓▓▓▓▓▓▓▒▒▓▓▓▓▓▓██▓▓▓▓▓▓▓▓██████▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒██
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓▓▓▓▓▓██░░▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░▓▓▓▓▓▓▓▓▓▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
        </pre>
      </v-col>
      
      <!-- ロゴ＆タイトル -->
      <v-col cols="12" md="8" class="text-center mb-8 position-relative" style="z-index: 2;">
        <h1 class="text-h2 font-weight-bold text-white mb-4" style="font-family: 'Libre Baskerville', serif;">
          SAPJP-pedia
        </h1>
        <p class="text-body-1 text-grey-lighten-1" style="font-family: 'Inter', sans-serif;">
          AIと人間が共創する、次世代のSAPナレッジベース
        </p>
      </v-col>

      <!-- 検索バー -->
      <v-col cols="12" md="7" lg="6">
        <v-text-field
          v-model="searchQuery"
          placeholder="Search for articles..."
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          bg-color="#1E1E1E"
          density="comfortable"
          rounded="lg"
          hide-details
          class="mb-8 search-bar"
          base-color="#333"
          color="primary"
          @keyup.enter="search"
          clearable
          @click:clear="clearSearch"
        >
          <template v-slot:append-inner>
            <div class="d-none d-sm-flex align-center ga-1 mr-2">
              <kbd class="key-hint">Ctrl</kbd>
              <span class="text-xs text-grey-darken-1">+</span>
              <kbd class="key-hint">K</kbd>
            </div>
          </template>
        </v-text-field>
      </v-col>

      <!-- 検索結果リスト -->
      <v-col cols="12" md="8" lg="7" v-if="articles.length > 0 || loading || searchQuery">
        <div v-if="loading" class="text-center py-8">
          <v-progress-circular indeterminate color="white" />
        </div>

        <div v-else-if="articles.length === 0 && searchQuery" class="text-center text-grey py-8">
          No articles found for "{{ searchQuery }}"
        </div>

        <v-list v-else bg-color="transparent" class="search-results">
          <v-list-item
            v-for="article in articles"
            :key="article.id"
            :to="`/articles/${article.id}`"
            class="mb-3 py-3 rounded-lg border-bottom-hover"
            lines="two"
          >
            <template v-slot:prepend>
              <v-icon color="grey-lighten-1" class="mr-4">mdi-file-document-outline</v-icon>
            </template>
            
            <v-list-item-title class="text-h6 font-weight-bold mb-1" style="font-family: 'Libre Baskerville', serif;">
              {{ article.title }}
            </v-list-item-title>
            
            <v-list-item-subtitle class="text-body-2 text-grey">
               <v-chip size="x-small" color="grey" variant="outlined" class="mr-2">
                {{ article.module || 'General' }}
               </v-chip>
               Last verified: {{ formatDate(article.last_verified_at) }}
            </v-list-item-subtitle>
            
            <template v-slot:append>
              <v-icon color="grey-darken-2" size="small">mdi-arrow-right</v-icon>
            </template>
          </v-list-item>
        </v-list>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { searchArticles } from '@/api'

const router = useRouter()
const searchQuery = ref('')
const searchInput = ref(null) // Ref for the input
const articles = ref([])
const loading = ref(false)

// 検索実行
const search = async () => {
  loading.value = true
  try {
    articles.value = await searchArticles(searchQuery.value)
  } catch (error) {
    console.error('検索エラー:', error)
  } finally {
    loading.value = false
  }
}

// 検索クリア
const clearSearch = () => {
  searchQuery.value = ''
  search()
}

// 記事詳細へ遷移
const goToArticle = (id) => {
  router.push(`/articles/${id}`)
}

// 日付フォーマット
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('ja-JP')
}

// キーボードショートカット処理
const handleKeydown = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    // v-text-field exposes 'focus' method on the component
    // We need to bind ref="searchInput" to v-text-field first
    // But since we can't easily edit the template ref in this single replace call without being careful,
    // let's try to focus by querySelector as a fallback or assume ref is bound in next step.
    // Actually, let's just use document.querySelector for simplicity here if ref is tricky across multiple edits.
    const input = document.querySelector('.search-bar input')
    if (input) input.focus()
  }
}

// 初期読み込み
onMounted(() => {
  search()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.search-bar :deep(.v-field__input) {
  font-size: 1rem;
  padding-top: 10px;
  padding-bottom: 10px;
  color: #e0e0e0;
}

.search-bar :deep(.v-field__outline) {
  display: none;
}

.key-hint {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  background-color: #2C2C2C;
  border: 1px solid #444;
  border-bottom-width: 2px;
  border-radius: 4px;
  padding: 2px 6px;
  color: #BDBDBD;
  box-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.border-bottom-hover {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: background-color 0.2s;
}

.border-bottom-hover:hover {
  background-color: rgba(255, 255, 255, 0.03);
}

.ascii-art {
  color: #888888 !important;
  background-color: transparent !important;
  display: inline-block;
  text-align: left;
  line-height: 1.0;
  font-family: 'Courier New', monospace;
  font-size: 0.55vw;
  white-space: pre;
  letter-spacing: -1px;
  opacity: 0.8;
  mask-image: radial-gradient(circle, rgba(0,0,0,1) 40%, rgba(0,0,0,0) 70%);
  -webkit-mask-image: radial-gradient(circle, rgba(0,0,0,1) 40%, rgba(0,0,0,0) 70%);
  animation: blackhole-spin 120s linear infinite, blackhole-pulse 16s ease-in-out infinite alternate;
}

@keyframes blackhole-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes blackhole-pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.05);
    opacity: 1.0;
    filter: brightness(1.5) contrast(1.2);
  }
}
</style>
