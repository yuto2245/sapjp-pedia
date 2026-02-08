<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Article;
use App\Models\RevisionReport;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class ArticleController extends Controller
{
    /**
     * 記事検索 API
     * GET /api/search?q={query}
     */
    public function search(Request $request): JsonResponse
    {
        $query = $request->input('q', '');

        $articles = Article::query()
            ->when($query, function ($q) use ($query) {
                $q->where('title', 'like', "%{$query}%")
                  ->orWhere('module', 'like', "%{$query}%")
                  ->orWhere('content', 'like', "%{$query}%");
            })
            ->where('status', 'published')
            ->select('id', 'title', 'module', 'last_verified_at')
            ->orderBy('updated_at', 'desc')
            ->get();

        return response()->json($articles);
    }

    /**
     * 記事詳細 API
     * GET /api/articles/{id}
     */
    public function show(string $id): JsonResponse
    {
        $article = Article::with('references')->findOrFail($id);

        return response()->json([
            'id' => $article->id,
            'title' => $article->title,
            'content' => $article->content,
            'module' => $article->module,
            'status' => $article->status,
            'last_verified_at' => $article->last_verified_at,
            'references' => $article->references->map(fn($ref) => [
                'id' => $ref->id,
                'type' => $ref->type,
                'title' => $ref->title,
                'url' => $ref->url,
            ]),
        ]);
    }

    /**
     * 修正履歴一覧 API
     * GET /api/articles/{id}/reports
     */
    public function reports(string $id): JsonResponse
    {
        $article = Article::findOrFail($id);

        $reports = $article->revisionReports()
            ->where('status', 'approved')
            ->orderBy('created_at', 'desc')
            ->get()
            ->map(fn($report) => [
                'id' => $report->id,
                'created_at' => $report->created_at,
                'creator_type' => $report->creator_type,
                'reason' => $report->reason,
                'status' => $report->status,
            ]);

        return response()->json($reports);
    }

    /**
     * 修正提案 API
     * POST /api/articles/{id}/propose
     */
    public function propose(Request $request, string $id): JsonResponse
    {
        $validated = $request->validate([
            'creator_type' => 'required|in:human,ai',
            'reason' => 'required|string',
            'after_content' => 'required|string',
            'reference_urls' => 'nullable|array',
        ]);

        $article = Article::findOrFail($id);

        $report = RevisionReport::create([
            'article_id' => $article->id,
            'creator_type' => $validated['creator_type'],
            'reason' => $validated['reason'],
            'before_content' => $article->content,
            'after_content' => $validated['after_content'],
            'status' => 'pending',
            'reference_ids' => $validated['reference_urls'] ?? [],
        ]);

        return response()->json([
            'message' => '修正提案を受け付けました',
            'report_id' => $report->id,
        ], 201);
    }

    // ========================================
    // 管理者用API（要認証）
    // ========================================

    /**
     * 記事作成 API
     * POST /api/articles
     */
    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'title' => 'required|string|max:255',
            'content' => 'required|string',
            'module' => 'nullable|string|max:100',
            'status' => 'nullable|in:draft,published,archived',
        ]);

        $article = Article::create([
            'title' => $validated['title'],
            'content' => $validated['content'],
            'module' => $validated['module'] ?? null,
            'status' => $validated['status'] ?? 'draft',
        ]);

        return response()->json([
            'message' => '記事を作成しました',
            'article' => $article,
        ], 201);
    }

    /**
     * 記事更新 API
     * PUT /api/articles/{id}
     */
    public function update(Request $request, string $id): JsonResponse
    {
        $validated = $request->validate([
            'title' => 'sometimes|string|max:255',
            'content' => 'sometimes|string',
            'module' => 'nullable|string|max:100',
            'status' => 'nullable|in:draft,published,archived',
        ]);

        $article = Article::findOrFail($id);
        $article->update($validated);

        return response()->json([
            'message' => '記事を更新しました',
            'article' => $article,
        ]);
    }

    /**
     * 記事削除 API
     * DELETE /api/articles/{id}
     */
    public function destroy(string $id): JsonResponse
    {
        $article = Article::findOrFail($id);
        $article->delete();

        return response()->json([
            'message' => '記事を削除しました',
        ]);
    }
}
