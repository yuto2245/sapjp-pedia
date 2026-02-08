<?php

use App\Http\Controllers\Api\ArticleController;
use App\Http\Controllers\Api\ReportController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
*/

// ========================================
// 認証不要のAPI（一般・AI向け）
// ========================================

// 記事検索
Route::get('/search', [ArticleController::class, 'search']);

// 記事詳細
Route::get('/articles/{id}', [ArticleController::class, 'show']);

// 修正履歴一覧
Route::get('/articles/{id}/reports', [ArticleController::class, 'reports']);

// 修正提案（誰でも提案可能）
Route::post('/articles/{id}/propose', [ArticleController::class, 'propose']);

// 修正レポート詳細
Route::get('/reports/{id}', [ReportController::class, 'show']);

// 記事作成（開発用：一時的に認証解除）
Route::post('/articles', [ArticleController::class, 'store']);

// 修正提案の管理（開発用：一時的に認証解除）
Route::get('/reports/pending', [ReportController::class, 'pending']);
Route::patch('/reports/{id}/approve', [ReportController::class, 'approve']);
Route::patch('/reports/{id}/reject', [ReportController::class, 'reject']);

// ========================================
// 認証済みユーザーのみ（管理者用）
// ========================================
Route::middleware('auth:sanctum')->group(function () {
    // 現在のユーザー情報
    Route::get('/user', function (Request $request) {
        return $request->user();
    });

    // 記事CRUD
    // Route::post('/articles', [ArticleController::class, 'store']);
    Route::put('/articles/{id}', [ArticleController::class, 'update']);
    Route::delete('/articles/{id}', [ArticleController::class, 'destroy']);

    // 修正提案の管理
    // Route::get('/reports/pending', [ReportController::class, 'pending']);
    // Route::patch('/reports/{id}/approve', [ReportController::class, 'approve']);
    // Route::patch('/reports/{id}/reject', [ReportController::class, 'reject']);
});
