<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Reference extends Model
{
    use HasUuids;

    protected $fillable = [
        'type',
        'url',
        'title',
        'description',
    ];

    /**
     * 参照先に紐づく記事
     */
    public function articles(): BelongsToMany
    {
        return $this->belongsToMany(Article::class, 'article_references')
            ->withTimestamps();
    }
}
