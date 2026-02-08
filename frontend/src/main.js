/**
 * main.js
 *
 * Bootstraps Vuetify, Router and other plugins then mounts the App
 */

// Plugins
import { registerPlugins } from '@/plugins'

// Components
import App from './App.vue'

// Router
import router from './router'

// Composables
import { createApp } from 'vue'

// Styles
import 'unfonts.css'
import '@/assets/main.css'

const app = createApp(App)

registerPlugins(app)

// ルーターを登録
app.use(router)

app.mount('#app')
