<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Article;
use App\Models\RevisionReport;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class ReportController extends Controller
{
    /**
     * 保留中の修正提案一覧
     * GET /api/reports/pending
     */
    public function pending(): JsonResponse
    {
        $reports = RevisionReport::with('article:id,title')
            ->where('status', 'pending')
            ->orderBy('created_at', 'desc')
            ->get()
            ->map(fn($report) => [
                'id' => $report->id,
                'article_id' => $report->article_id,
                'article_title' => $report->article?->title,
                'creator_type' => $report->creator_type,
                'reason' => $report->reason,
                'status' => $report->status,
                'created_at' => $report->created_at,
            ]);

        return response()->json($reports);
    }

    /**
     * 修正レポート詳細
     * GET /api/reports/{id}
     */
    public function show(string $id): JsonResponse
    {
        $report = RevisionReport::with('article:id,title')->findOrFail($id);

        return response()->json([
            'id' => $report->id,
            'article_id' => $report->article_id,
            'article_title' => $report->article?->title,
            'creator_type' => $report->creator_type,
            'reason' => $report->reason,
            'before_content' => $report->before_content,
            'after_content' => $report->after_content,
            'status' => $report->status,
            'reference_ids' => $report->reference_ids,
            'created_at' => $report->created_at,
            'processed_at' => $report->processed_at,
        ]);
    }

    /**
     * 修正提案を承認
     * PATCH /api/reports/{id}/approve
     * 
     * 承認すると記事の内容が after_content に更新される
     */
    public function approve(string $id): JsonResponse
    {
        $report = RevisionReport::findOrFail($id);

        if ($report->status !== 'pending') {
            return response()->json([
                'message' => 'この提案は既に処理されています',
            ], 400);
        }

        // 記事の内容を更新
        $article = Article::findOrFail($report->article_id);
        $article->update([
            'content' => $report->after_content,
        ]);

        // 参考文献の保存と紐付け
        if (!empty($report->reference_ids)) {
            $refIds = [];
            foreach ($report->reference_ids as $url) {
                // URLからReferenceを取得または作成
                // タイトルは仮でURLを設定（本来はスクレイピングやAI解析で取得したい）
                $reference = \App\Models\Reference::firstOrCreate(
                    ['url' => $url],
                    [
                        'title' => $url,
                        'type' => $report->creator_type === 'ai' ? 'ai_generated' : 'community_blog',
                        'description' => 'Automatically added via revision approval',
                    ]
                );
                $refIds[] = $reference->id;
            }

            // 記事に紐付け（重複を避けるためsyncWithoutDetachingを使用）
            $article->references()->syncWithoutDetaching($refIds);
        }

        // レポートのステータスを更新
        $report->update([
            'status' => 'approved',
            'processed_at' => now(),
        ]);

        return response()->json([
            'message' => '修正提案を承認し、記事と参考文献を更新しました',
            'report_id' => $report->id,
            'article_id' => $article->id,
        ]);
    }

    /**
     * 修正提案を却下
     * PATCH /api/reports/{id}/reject
     */
    public function reject(string $id): JsonResponse
    {
        $report = RevisionReport::findOrFail($id);

        if ($report->status !== 'pending') {
            return response()->json([
                'message' => 'この提案は既に処理されています',
            ], 400);
        }

        $report->update([
            'status' => 'rejected',
            'processed_at' => now(),
        ]);

        return response()->json([
            'message' => '修正提案を却下しました',
            'report_id' => $report->id,
        ]);
    }
}
