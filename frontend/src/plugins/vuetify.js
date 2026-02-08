/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com
 */

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Composables
import { createVuetify } from 'vuetify'

const grokDark = {
  dark: true,
  colors: {
    background: '#0a0a0a', // より深い黒
    surface: '#121212',    // わずかに明るい黒
    primary: '#FFFFFF',    // メインカラーは白（テキスト）
    secondary: '#424242',
    accent: '#64B5F6',     // リンク色などのアクセント（淡い青）
    error: '#CF6679',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FFB74D',
  },
}

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    defaultTheme: 'grokDark',
    themes: {
      grokDark,
    },
  },
})
