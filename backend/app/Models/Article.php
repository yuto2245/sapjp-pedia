<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;
use App\Models\FactCheck;

class Article extends Model
{
    use HasUuids;

    protected $fillable = [
        'title',
        'content',
        'module',
        'status',
        'last_verified_at',
    ];

    protected $casts = [
        'last_verified_at' => 'datetime',
    ];

    /**
     * 記事に紐づく参照先
     */
    public function references(): BelongsToMany
    {
        return $this->belongsToMany(Reference::class, 'article_references')
            ->withTimestamps();
    }

    /**
     * 記事に紐づく修正レポート
     */
    public function revisionReports(): HasMany
    {
        return $this->hasMany(RevisionReport::class);
    }

    /**
     * 記事に紐づくファクトチェック
     */
    public function factChecks(): HasMany
    {
        return $this->hasMany(FactCheck::class);
    }
}
