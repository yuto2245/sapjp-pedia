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
        <v-col class="d-none d-md-block" style="width: 400px; flex: 0 0 400px;">
          <div class="sticky-top pt-12 pl-4">
             <div class="text-body-2 text-grey text-uppercase mb-4 font-weight-bold" style="letter-spacing: 1px;">
              目次
             </div>
             <div class="pl-2 border-l-2 border-opacity-25" style="border-color: #424242;">
               <div v-if="tableOfContents.length === 0" class="text-body-2 text-grey">
                 見出しがありません
               </div>
               <a
                 v-for="item in tableOfContents"
                 :key="item.id"
                 class="toc-link text-body-2"
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
            <!-- タイトル＆アクションボタン -->
            <div class="d-flex align-start justify-space-between mb-4">
              <h1 class="text-h4 font-weight-bold text-white" style="font-family: 'Libre Baskerville', serif; line-height: 1.2;">
                {{ article.title }}
              </h1>
              <div class="d-flex align-center ml-4" style="flex-shrink: 0;">
                 <ThemeButton
                   class="mr-3"
                   prepend-icon="mdi-history"
                   :to="`/articles/${route.params.id}/history`"
                 >
                   履歴
                 </ThemeButton>
                 <ThemeButton
                   prepend-icon="mdi-pencil"
                   :to="`/articles/${route.params.id}/propose`"
                 >
                   編集
                 </ThemeButton>
              </div>
            </div>

            <!-- メタデータ -->
            <div class="d-flex align-center mb-10 pb-4 border-b" style="border-color: #333 !important;">
               <v-chip size="small" variant="outlined" color="grey" class="mr-4 font-weight-bold">
                  {{ article.module || 'General' }}
               </v-chip>
               <div class="d-flex align-center text-caption text-grey">
                  <v-icon size="small" class="mr-1" :color="freshnessColor">mdi-check-decagram</v-icon>
                  <span :class="`text-${freshnessColor}`">{{ freshnessText }}</span>
               </div>
            </div>

            <!-- 本文 -->
            <div class="markdown-body position-relative mb-16">
              <div v-html="renderedContent" @mouseover="handleMouseOver" @click="handleEvidenceClick" />
              
              <!-- 証拠ポップアップ -->
              <v-card
                v-if="hoveredEvidence"
                class="evidence-popup rounded-custom border"
                elevation="8"
                min-width="250"
                max-width="320"
                theme="dark"
                :style="{ top: popupPos.y + 'px', left: popupPos.x + 'px', position: 'absolute', zIndex: 100, borderColor: '#424242 !important' }"
                @mouseleave="closePopup"
              >
                <div class="pa-3">
                  <!-- Header Link -->
                  <a 
                    :href="hoveredEvidence.url" 
                    target="_blank" 
                    class="d-flex align-center text-decoration-none text-white mb-1 hover-link"
                  >
                    <span class="text-body-2 font-weight-bold text-truncate">{{ hoveredEvidence.title || hoveredEvidence.url }}</span>
                    <v-icon size="x-small" class="ml-1 text-grey-darken-1">mdi-open-in-new</v-icon>
                  </a>

                  <!-- Quote -->
                  <div class="text-caption font-italic text-grey-lighten-1 mt-1" style="line-height: 1.4;">
                     "{{ hoveredEvidence.quote }}"
                  </div>
                </div>
              </v-card>
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
import ThemeButton from '@/components/ThemeButton.vue'

const route = useRoute()
const router = useRouter()
const article = ref(null)
const loading = ref(true)
const tableOfContents = ref([])

// Popup state
const hoveredEvidence = ref(null)
const popupPos = ref({ x: 0, y: 0 })

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
  const content = article.value?.fact_check?.synthesized_text || article.value?.content
  if (!content) return
  
  const lines = content.split('\n')
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

// Markdown レンダリング
const renderedContent = computed(() => {
  const content = article.value?.fact_check?.synthesized_text || article.value?.content
  if (!content) return ''
  
  const renderer = new marked.Renderer()
  let idCounter = 0
  
  renderer.heading = ({ text, depth }) => {
    const id = `heading-${idCounter++}`
    return `<h${depth} id="${id}">${text}</h${depth}>`
  }

  let html = marked.parse(content, { renderer })

  // [n] を置換 (FactCheckがある場合のみ)
  if (article.value?.fact_check) {
    html = html.replace(/\[(\d+)\]/g, (match, num) => {
      // 証拠が存在するか確認
      const exists = article.value.fact_check.evidences.some(e => e.reference_num == num)
      if (exists) {
        return `<span class="evidence-ref" data-ref="${num}">[${num}]</span>`
      }
      return match
    })
  }

  return html
})

// マウスオーバー処理
const handleMouseOver = (e) => {
  const target = e.target.closest('.evidence-ref')
  if (target) {
    const refNum = target.dataset.ref
    const evidence = article.value.fact_check?.evidences.find(ev => ev.reference_num == refNum)
    
    if (evidence) {
      hoveredEvidence.value = evidence
      // 座標計算 (要素の直下)
      const rect = target.getBoundingClientRect()
      // 親コンテナ(.markdown-body)相対座標に変換
      const container = e.currentTarget.getBoundingClientRect()
      
      popupPos.value = {
        x: rect.left - container.left, // 左端合わせ
        y: rect.bottom - container.top + 8 // 下に8px
      }
    }
  } else if (!e.target.closest('.evidence-popup')) {
    // ポップアップ以外にマウスが行ったら閉じる（ただしポップアップへの移動は許容したいのでmouseleaveで閉じる制御が必要かも）
    // 今回は単純化のため、refから外れたら閉じるが、ポップアップ自体へのホバーも考慮するならロジック追加が必要
    // -> v-menu的な挙動にするにはもう少し工夫がいる。
    // 親の@clickのみにする手もあるが、ホバー要望。
    // 一旦、popup自体にはマウスイベントを伝播させないようにし、記事本文のホバーでターゲットが変わったら閉じるようにする。
  }
}

// ポップアップを閉じる
const closePopup = () => {
  hoveredEvidence.value = null
}

// クリックでも開くように（モバイル対応など）
const handleEvidenceClick = (e) => {
  handleMouseOver(e)
}

// スクロール処理
const scrollToHeading = (id) => {
  const element = document.getElementById(id)
  if (element) {
    const headerOffset = 80
    const elementPosition = element.getBoundingClientRect().top
    const offsetPosition = elementPosition + window.pageYOffset - headerOffset

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    })
  }
}

// 鮮度表示 (FactCheckがある場合はその日付を優先)
const freshnessColor = computed(() => {
  const dateStr = article.value?.fact_check?.updated_at || article.value?.last_verified_at
  if (!dateStr) return 'grey'
  const hours = (Date.now() - new Date(dateStr)) / (1000 * 60 * 60)
  if (hours < 24) return 'success'
  if (hours < 72) return 'warning'
  return 'error'
})

const freshnessText = computed(() => {
  const dateStr = article.value?.fact_check?.last_checked_at || article.value?.last_verified_at
  if (!dateStr) return '未検証'
  const date = new Date(dateStr)
  return `Verified by Grokipedia (${date.toLocaleDateString('ja-JP')})`
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


</script>

<style scoped>
:deep(.markdown-body h2) {
  margin-top: 3rem;
  margin-bottom: 1rem;
}

:deep(.markdown-body h3) {
  margin-top: 2.5rem;
  margin-bottom: 0.75rem;
}

:deep(.markdown-body p) {
  margin-bottom: 1rem;
}

.sticky-top {
  position: sticky;
  top: 64px;
}

.hover-link {
  border-bottom: none !important;
  color: inherit !important;
}

.rounded-custom {
  border-radius: 16px;
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
  color: #9e9e9e;
  text-decoration: none;
  display: block;
  padding: 4px 0;
  transition: color 0.2s;
  cursor: pointer;
}

.toc-link:hover {
  color: #E0E0E0;
}

/* Evidence Reference Styles */
:deep(.evidence-ref) {
  color: #64B5F6; /* Primary Color */
  font-weight: bold;
  cursor: pointer;
  margin: 0 2px;
  font-size: 0.8em;
  vertical-align: super;
  transition: opacity 0.2s;
}

:deep(.evidence-ref:hover) {
  opacity: 0.8;
  text-decoration: underline;
}

.hover-source:hover {
  opacity: 0.8;
}
</style>
