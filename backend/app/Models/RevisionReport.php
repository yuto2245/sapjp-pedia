<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class RevisionReport extends Model
{
    use HasUuids;

    protected $fillable = [
        'article_id',
        'creator_type',
        'reason',
        'before_content',
        'after_content',
        'status',
        'reference_ids',
        'processed_at',
    ];

    protected $casts = [
        'reference_ids' => 'array',
        'processed_at' => 'datetime',
    ];

    /**
     * 修正レポートに紐づく記事
     */
    public function article(): BelongsTo
    {
        return $this->belongsTo(Article::class);
    }
}
