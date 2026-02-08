import axios from 'axios'

// APIクライアントの設定
const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
})

// 記事検索
export const searchArticles = async (query = '') => {
    const response = await api.get('/search', { params: { q: query } })
    return response.data
}

// 記事詳細取得
export const getArticle = async (id) => {
    const response = await api.get(`/articles/${id}`)
    return response.data
}

// 記事作成
export const createArticle = async (data) => {
    const response = await api.post('/articles', data)
    return response.data
}

// 修正履歴取得
export const getArticleReports = async (id) => {
    const response = await api.get(`/articles/${id}/reports`)
    return response.data
}

// 修正レポート詳細取得 (New)
export const getReport = async (id) => {
    const response = await api.get(`/reports/${id}`)
    return response.data
}

// 修正提案
export const proposeRevision = async (id, data) => {
    const response = await api.post(`/articles/${id}/propose`, data)
    return response.data
}

// 管理者用API（今回は認証なしで通るルートのみ使用）
// 保留中の提案一覧
export const getPendingReports = async () => {
    const response = await api.get('/reports/pending')
    return response.data
}

// 提案承認
export const approveReport = async (id) => {
    const response = await api.patch(`/reports/${id}/approve`)
    return response.data
}

// 提案却下
export const rejectReport = async (id) => {
    const response = await api.patch(`/reports/${id}/reject`)
    return response.data
}

export default api
