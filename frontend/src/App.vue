<template>
  <v-app>
    <!-- ナビゲーションバー -->
    <v-app-bar color="rgba(15, 15, 15, 0.9)" flat class="border-b" density="comfortable" style="backdrop-filter: blur(10px);">
      <v-container class="d-flex align-center py-0">
        <router-link to="/" class="text-decoration-none d-flex align-center">
          <span class="text-h5 font-weight-bold text-white" style="font-family: 'Libre Baskerville', serif;">
            SAPJP-pedia
          </span>
          <v-chip size="x-small" color="white" variant="outlined" class="ml-2 font-weight-bold" style="border-color: rgba(255,255,255,0.3);">
            Beta
          </v-chip>
        </router-link>

        <v-spacer />

        <v-btn
          prepend-icon="mdi-plus"
          to="/editor"
          variant="text"
          class="text-capitalize"
        >
          New Article
        </v-btn>

        <v-btn
          prepend-icon="mdi-shield-account"
          to="/admin"
          variant="text"
          color="grey-lighten-1"
          class="text-capitalize"
        >
          Admin
        </v-btn>

        <v-btn
          prepend-icon="mdi-api"
          to="/developer/api"
          variant="text"
          color="grey-lighten-1"
          class="text-capitalize"
        >
          API
        </v-btn>
      </v-container>
    </v-app-bar>

    <!-- メインコンテンツ -->
    <v-main>
      <router-view />
    </v-main>

    <!-- フッター -->
    <v-footer class="bg-transparent border-t mt-8">
      <v-container>
        <div class="d-flex justify-space-between align-center">
          <p class="text-caption text-grey mb-0">
            © 2026 SAPJP-pedia
          </p>
          <div class="text-caption text-grey">
            Powered by Gemini 2.0 Flash & Laravel 11
          </div>
        </div>
      </v-container>
    </v-footer>
  </v-app>
</template>

<script setup>
//
</script>
