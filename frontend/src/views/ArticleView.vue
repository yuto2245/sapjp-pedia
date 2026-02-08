<template>
  <v-container class="py-12" fluid>
    <!-- ローディング -->
    <v-row v-if="loading" justify="center" class="mt-8">
      <v-progress-circular indeterminate color="primary" size="64" />
    </v-row>

    <!-- 記事詳細 -->
    <template v-else-if="article">
      <v-row>
        <!-- 左サイドバー（目次・メタ情報） -->
        <v-col class="d-none d-md-block" style="width: 450px; flex: 0 0 450px;">
          <div class="sticky-top pt-12 pl-4">
             <div class="text-caption text-grey text-uppercase mb-4 font-weight-bold" style="letter-spacing: 1px;">
              目次
             </div>
             <div class="pl-2 border-l-2 border-opacity-25" style="border-color: #424242;">
               <div v-if="tableOfContents.length === 0" class="text-caption text-grey">
                 見出しがありません
               </div>
               <a
                 v-for="item in tableOfContents"
                 :key="item.id"
                 class="toc-link text-caption"
                 :style="{ paddingLeft: (item.level - 1) * 8 + 'px' }"
                 @click.prevent="scrollToHeading(item.id)"
               >
                 {{ item.text }}
               </a>
             </div>
          </div>
        </v-col>

        <!-- メインコンテンツ -->
        <v-col class="flex-grow-1" style="min-width: 0;">
          <div style="max-width: 1280px; padding-right: 24px;">
            <!-- タイトル -->
            <h1 class="text-h2 font-weight-bold mb-4 text-white" style="font-family: 'Libre Baskerville', serif; line-height: 1.2;">
              {{ article.title }}
            </h1>

            <!-- メタデータ＆アクションバー -->
            <div class="d-flex flex-wrap align-center mb-10 pb-4 border-b" style="border-color: #333 !important;">
               <!-- 左側：メタ情報 -->
               <div class="d-flex align-center mr-auto">
                 <v-chip size="small" variant="outlined" color="primary" class="mr-4 font-weight-bold">
                    {{ article.module || 'General' }}
                 </v-chip>
                 
                 <div class="d-flex align-center text-caption text-grey mr-6">
                    <v-icon size="small" class="mr-1" :color="freshnessColor">mdi-check-decagram</v-icon>
                    <span :class="`text-${freshnessColor}`">{{ freshnessText }}</span>
                 </div>
                 
                 <div class="d-flex align-center text-caption text-grey">
                    <v-icon size="small" class="mr-1">mdi-clock-outline</v-icon>
                    <span>5 min read</span>
                 </div>
               </div>

               <!-- 右側：アクションボタン -->
               <div class="d-flex align-center">
                 <v-btn
                   variant="text"
                   density="comfortable"
                   color="grey"
                   class="text-capitalize mr-2"
                   prepend-icon="mdi-history"
                   :to="`/articles/${route.params.id}/history`"
                 >
                   History
                 </v-btn>
                 
                 <v-btn
                   variant="outlined"
                   density="comfortable"
                   color="primary"
                   class="text-capitalize"
                   prepend-icon="mdi-pencil"
                   :to="`/articles/${route.params.id}/propose`"
                 >
                   Edit
                 </v-btn>
               </div>
            </div>

            <!-- 概要（リード文） -->
             <p class="text-h6 text-grey-lighten-1 mb-10 font-weight-regular" style="font-family: 'Inter', sans-serif; line-height: 1.6;">
               {{ article.title }} は SAP ERP における重要なコンポーネントです... (概要プレースホルダー)
             </p>

            <!-- 本文 -->
            <div class="markdown-body">
              <div v-html="renderedContent" />
            </div>

            <!-- 参考文献セクション -->
            <div v-if="article.references?.length > 0" class="mt-16 pt-8 border-t" style="border-color: #333 !important;">
              <h3 class="text-h4 font-weight-bold mb-6 text-white" style="font-family: 'Libre Baskerville', serif;">
                参考文献
              </h3>
              <div class="reference-list">
                <div v-for="(ref, index) in article.references" :key="ref.id" class="mb-3">
                  <span class="text-grey mr-3">{{ index + 1 }}.</span>
                  <a :href="ref.url" target="_blank" rel="noopener noreferrer" class="text-decoration-none hover-link">
                    <span class="text-body-2 text-grey-lighten-3">{{ ref.title || ref.url }}</span>
                    <span class="text-caption text-grey-darken-1 ml-2">{{ getDomain(ref.url) }}</span>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </v-col>
        
        <!-- 右サイドバーは削除 -->
      </v-row>
    </template>

    <!-- エラー -->
    <v-alert v-else type="error" class="mt-8" variant="tonal">
      記事が見つかりませんでした。
      <template v-slot:append>
        <v-btn variant="text" to="/">トップへ戻る</v-btn>
      </template>
    </v-alert>
  </v-container>
</template>


<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getArticle } from '@/api'
import { marked } from 'marked'

const route = useRoute()
const router = useRouter()
const article = ref(null)
const loading = ref(true)
const tableOfContents = ref([])

// 記事取得
const fetchArticle = async () => {
  loading.value = true
  try {
    article.value = await getArticle(route.params.id)
    generateToC()
  } catch (error) {
    console.error('記事取得エラー:', error)
    article.value = null
  } finally {
    loading.value = false
  }
}

// 目次生成
const generateToC = () => {
  if (!article.value?.content) return
  
  const lines = article.value.content.split('\n')
  const toc = []
  let idCounter = 0

  lines.forEach(line => {
    const match = line.match(/^(#{1,3})\s+(.+)$/)
    if (match) {
      const level = match[1].length
      const text = match[2].trim()
      const id = `heading-${idCounter++}`
      toc.push({ id, text, level })
    }
  })
  tableOfContents.value = toc
}

// Markdown レンダリング (ID付与対応)
const renderedContent = computed(() => {
  if (!article.value?.content) return ''
  
  const renderer = new marked.Renderer()
  let idCounter = 0
  
  renderer.heading = ({ text, depth }) => {
    const id = `heading-${idCounter++}`
    return `<h${depth} id="${id}">${text}</h${depth}>`
  }

  return marked.parse(article.value.content, { renderer })
})

// スクロール処理
const scrollToHeading = (id) => {
  const element = document.getElementById(id)
  if (element) {
    const headerOffset = 80 // ヘッダー分など
    const elementPosition = element.getBoundingClientRect().top
    const offsetPosition = elementPosition + window.pageYOffset - headerOffset

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    })
  }
}

// 鮮度表示
const freshnessColor = computed(() => {
  if (!article.value?.last_verified_at) return 'grey'
  const hours = (Date.now() - new Date(article.value.last_verified_at)) / (1000 * 60 * 60)
  if (hours < 24) return 'success'
  if (hours < 72) return 'warning'
  return 'error'
})

const freshnessText = computed(() => {
  if (!article.value?.last_verified_at) return '未検証'
  const date = new Date(article.value.last_verified_at)
  return `AI検証済み (${date.toLocaleDateString('ja-JP', { year: 'numeric', month: '2-digit', day: '2-digit' })})`
})

const getDomain = (url) => {
  try {
    return new URL(url).hostname
  } catch {
    return ''
  }
}

onMounted(() => {
  fetchArticle()
})

const formatRefType = (type) => {
  const map = {
    official_doc: 'Official Doc',
    community_blog: 'Community Blog',
    personal_experience: 'Experience',
    ai_generated: 'AI Generated'
  }
  return map[type] || type
}
</script>

<style scoped>
.sticky-top {
  position: sticky;
  top: 64px;
}

.hover-link:hover .text-body-2 {
  color: #64B5F6 !important;
  text-decoration: underline;
}

.article-content h1 {
  font-size: 1.8rem;
  margin: 2rem 0 1rem;
  font-weight: bold;
}

/* 目次リンクのスタイル */
.toc-link {
  color: #9e9e9e; /* text-grey-darken-1 */
  text-decoration: none;
  display: block;
  padding: 4px 0;
  transition: color 0.2s;
  cursor: pointer;
}

.toc-link:hover {
  color: #E0E0E0; /* text-white */
}

</style>
