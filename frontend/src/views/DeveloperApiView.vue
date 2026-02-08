<template>
  <v-container class="py-12">
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        <div class="d-flex align-center mb-8">
          <v-btn icon="mdi-arrow-left" variant="text" @click="router.back()" color="grey" class="mr-4" />
          <h1 class="text-h4 font-weight-bold" style="font-family: 'Libre Baskerville', serif;">
            開発者用 API
          </h1>
        </div>

        <div class="mb-12">
          <p class="text-body-1 text-grey-lighten-1 mb-6" style="line-height: 1.8;">
            SAPJP-pedia のナレッジベースを活用して、強力なアプリケーションを構築しましょう。<br>
            記事へのアクセス、検索、編集提案をプログラムからシームレスに行えます。
          </p>
          
          <div class="bg-black border rounded px-4 py-3 d-flex align-center" style="border-color: #333 !important;">
            <span class="text-grey mr-4 text-caption text-uppercase font-weight-bold">Base URL</span>
            <code class="text-primary font-monospace" style="background: transparent;">http://127.0.0.1:8000/api</code>
          </div>
        </div>

        <!-- System Architecture -->
        <h2 class="text-h5 font-weight-bold mb-6 text-white" style="font-family: 'Libre Baskerville', serif;">
          システムアーキテクチャ
        </h2>
        
        <v-row class="mb-8">
          <v-col cols="12" md="4">
            <v-card class="h-100 border" style="border-color: #333 !important; background-color: #121212;">
              <v-card-text>
                <div class="d-flex align-center mb-3">
                  <v-icon color="green" class="mr-2">mdi-monitor-dashboard</v-icon>
                  <div class="font-weight-bold">Frontend</div>
                </div>
                <div class="text-caption text-grey">
                  Vue.js (Vuetify)<br>
                  SPA (Single Page Application)
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
             <v-card class="h-100 border" style="border-color: #333 !important; background-color: #121212;">
              <v-card-text>
                <div class="d-flex align-center mb-3">
                  <v-icon color="blue" class="mr-2">mdi-server-network</v-icon>
                  <div class="font-weight-bold">Backend API</div>
                </div>
                <div class="text-caption text-grey">
                  Laravel (PHP)<br>
                  RESTful API
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
             <v-card class="h-100 border" style="border-color: #333 !important; background-color: #121212;">
              <v-card-text>
                <div class="d-flex align-center mb-3">
                  <v-icon color="purple" class="mr-2">mdi-robot</v-icon>
                  <div class="font-weight-bold">AI Agent</div>
                </div>
                <div class="text-caption text-grey">
                  Python + Gemini API<br>
                  Automated Fact Checking
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Database Schema -->
        <h2 class="text-h5 font-weight-bold mb-6 text-white" style="font-family: 'Libre Baskerville', serif;">
          データベーススキーマ
        </h2>

        <v-expansion-panels variant="accordion" class="mb-12 border rounded" style="border-color: #333 !important; background-color: #121212;">
          <v-expansion-panel bg-color="#121212">
            <v-expansion-panel-title class="text-white">
              <v-icon icon="mdi-database" class="mr-3 text-grey" />
              articles（記事）
            </v-expansion-panel-title>
            <v-expansion-panel-text>
               <v-table density="compact" class="bg-transparent text-caption">
                <thead><tr><th>Column</th><th>Type</th><th>Description</th></tr></thead>
                <tbody>
                  <tr><td class="text-primary font-monospace">id</td><td>UUID</td><td>Primary Key</td></tr>
                  <tr><td class="text-primary font-monospace">title</td><td>String</td><td>記事タイトル</td></tr>
                  <tr><td class="text-primary font-monospace">content</td><td>Text</td><td>Markdown形式の本文</td></tr>
                  <tr><td class="text-primary font-monospace">module</td><td>String</td><td>SAPモジュール (MM, SD, etc.)</td></tr>
                  <tr><td class="text-primary font-monospace">status</td><td>Enum</td><td>draft / published / archived</td></tr>
                  <tr><td class="text-primary font-monospace">last_verified_at</td><td>Timestamp</td><td>AIまたは人による最終検証日時</td></tr>
                </tbody>
              </v-table>
            </v-expansion-panel-text>
          </v-expansion-panel>

          <v-expansion-panel bg-color="#121212">
            <v-expansion-panel-title class="text-white">
              <v-icon icon="mdi-file-document-edit" class="mr-3 text-grey" />
              reports（修正提案）
            </v-expansion-panel-title>
             <v-expansion-panel-text>
               <v-table density="compact" class="bg-transparent text-caption">
                <thead><tr><th>Column</th><th>Type</th><th>Description</th></tr></thead>
                <tbody>
                  <tr><td class="text-primary font-monospace">id</td><td>UUID</td><td>Primary Key</td></tr>
                  <tr><td class="text-primary font-monospace">article_id</td><td>UUID</td><td>対象記事のID</td></tr>
                  <tr><td class="text-primary font-monospace">content</td><td>Text</td><td>修正後のMarkdown本文</td></tr>
                  <tr><td class="text-primary font-monospace">reason</td><td>String</td><td>修正提案の理由</td></tr>
                  <tr><td class="text-primary font-monospace">status</td><td>Enum</td><td>pending / approved / rejected</td></tr>
                  <tr><td class="text-primary font-monospace">creator_type</td><td>Enum</td><td>human / ai</td></tr>
                </tbody>
              </v-table>
            </v-expansion-panel-text>
          </v-expansion-panel>

           <v-expansion-panel bg-color="#121212">
            <v-expansion-panel-title class="text-white">
              <v-icon icon="mdi-link-variant" class="mr-3 text-grey" />
              references（参考文献）
            </v-expansion-panel-title>
             <v-expansion-panel-text>
               <v-table density="compact" class="bg-transparent text-caption">
                <thead><tr><th>Column</th><th>Type</th><th>Description</th></tr></thead>
                <tbody>
                  <tr><td class="text-primary font-monospace">id</td><td>UUID</td><td>Primary Key</td></tr>
                  <tr><td class="text-primary font-monospace">article_id</td><td>UUID</td><td>対象記事のID</td></tr>
                  <tr><td class="text-primary font-monospace">title</td><td>String</td><td>ページタイトル</td></tr>
                  <tr><td class="text-primary font-monospace">url</td><td>String</td><td>URL</td></tr>
                  <tr><td class="text-primary font-monospace">type</td><td>Enum</td><td>official_doc / community_blog / etc.</td></tr>
                </tbody>
              </v-table>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>

        <!-- Endpoints -->
        <h2 class="text-h5 font-weight-bold mb-6 text-white" style="font-family: 'Libre Baskerville', serif;">
          エンドポイント
        </h2>

        <!-- GET /search -->
        <v-card class="mb-6 border" style="border-color: #333 !important; background-color: #121212;">
          <v-card-text>
            <div class="d-flex align-center mb-4">
              <v-chip color="blue" variant="tonal" size="small" class="font-weight-bold mr-3 rounded">GET</v-chip>
              <span class="text-h6 font-monospace text-white">/search</span>
            </div>
            <p class="text-body-2 text-grey mb-4">
              キーワードやモジュールで記事を検索します。
            </p>

            <div class="text-caption text-uppercase text-grey font-weight-bold mb-2">クエリパラメータ</div>
            <v-table density="compact" class="bg-transparent mb-6 text-body-2">
              <tbody>
                <tr>
                  <td class="font-monospace text-primary" width="120">q</td>
                  <td class="text-grey">任意。検索キーワード。</td>
                </tr>
              </tbody>
            </v-table>

            <div class="text-caption text-uppercase text-grey font-weight-bold mb-2">レスポンス例</div>
            <div class="bg-black pa-4 rounded border" style="border-color: #333 !important;">
              <pre class="font-monospace text-grey-lighten-2 text-caption" style="line-height: 1.5;">[
  {
    "id": "uuid-string...",
    "title": "S/4HANA MM 期間更新",
    "module": "MM",
    "last_verified_at": "2026-02-08T12:00:00Z"
  }
]</pre>
            </div>
          </v-card-text>
        </v-card>

        <!-- GET /articles/{id} -->
        <v-card class="mb-6 border" style="border-color: #333 !important; background-color: #121212;">
          <v-card-text>
            <div class="d-flex align-center mb-4">
              <v-chip color="blue" variant="tonal" size="small" class="font-weight-bold mr-3 rounded">GET</v-chip>
              <span class="text-h6 font-monospace text-white">/articles/{id}</span>
            </div>
            <p class="text-body-2 text-grey mb-4">
              指定された記事の詳細情報を取得します。
            </p>

            <div class="text-caption text-uppercase text-grey font-weight-bold mb-2">レスポンス例</div>
            <div class="bg-black pa-4 rounded border" style="border-color: #333 !important;">
              <pre class="font-monospace text-grey-lighten-2 text-caption" style="line-height: 1.5;">{
  "id": "uuid-string...",
  "title": "S/4HANA MM 期間更新",
  "content": "# Markdown コンテンツ...",
  "module": "MM",
  "status": "published",
  "last_verified_at": "2026-02-08T12:00:00Z",
  "references": [
    {
      "type": "official_doc",
      "title": "SAP Help Portal",
      "url": "https://help.sap.com/..."
    }
  ]
}</pre>
            </div>
          </v-card-text>
        </v-card>

        <!-- POST /articles/{id}/propose -->
        <v-card class="mb-6 border" style="border-color: #333 !important; background-color: #121212;">
          <v-card-text>
            <div class="d-flex align-center mb-4">
              <v-chip color="green" variant="tonal" size="small" class="font-weight-bold mr-3 rounded">POST</v-chip>
              <span class="text-h6 font-monospace text-white">/articles/{id}/propose</span>
            </div>
            <p class="text-body-2 text-grey mb-4">
              記事の修正提案を送信します。
            </p>

            <div class="text-caption text-uppercase text-grey font-weight-bold mb-2">リクエストボディ</div>
            <div class="bg-black pa-4 rounded border mb-6" style="border-color: #333 !important;">
              <pre class="font-monospace text-grey-lighten-2 text-caption" style="line-height: 1.5;">{
  "creator_type": "human",
  "reason": "2025年リリースに合わせて更新",
  "after_content": "# 更新後の Markdown コンテンツ...",
  "reference_urls": [
    "https://example.com/new-source"
  ]
}</pre>
            </div>

            <div class="text-caption text-uppercase text-grey font-weight-bold mb-2">成功レスポンス (201 Created)</div>
            <div class="bg-black pa-4 rounded border" style="border-color: #333 !important;">
              <pre class="font-monospace text-grey-lighten-2 text-caption" style="line-height: 1.5;">{
  "message": "修正提案を受け付けました",
  "report_id": "uuid-string..."
}</pre>
            </div>
          </v-card-text>
        </v-card>

        <!-- PATCH /reports/{id}/approve -->
        <v-card class="mb-6 border" style="border-color: #333 !important; background-color: #121212;">
          <v-card-text>
            <div class="d-flex align-center mb-4">
              <v-chip color="orange" variant="tonal" size="small" class="font-weight-bold mr-3 rounded">PATCH</v-chip>
              <span class="text-h6 font-monospace text-white">/reports/{id}/approve</span>
            </div>
            <p class="text-body-2 text-grey mb-4">
              修正提案を承認し、記事を更新します。管理者権限が必要です。
            </p>

            <div class="text-caption text-uppercase text-grey font-weight-bold mb-2">成功レスポンス (200 OK)</div>
            <div class="bg-black pa-4 rounded border" style="border-color: #333 !important;">
              <pre class="font-monospace text-grey-lighten-2 text-caption" style="line-height: 1.5;">{
  "message": "修正提案を承認し、記事と参考文献を更新しました",
  "report_id": "uuid...",
  "article_id": "uuid..."
}</pre>
            </div>
          </v-card-text>
        </v-card>

      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<style scoped>
.font-monospace {
  font-family: 'Fira Code', monospace;
}
</style>
