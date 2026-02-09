<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use App\Models\Article;
use App\Models\Evidence;
use App\Models\EvidenceChain;

class FactCheck extends Model
{
    use HasFactory;

    protected $fillable = [
        'article_id',
        'status',
        'assertion_text',
        'synthesized_text',
        'nlc_score',
        'conductivity',
        'dignity_score',
        'evidence_count',
        'last_checked_at'
    ];

    protected $casts = [
        'last_checked_at' => 'datetime',
        'nlc_score' => 'decimal:4',
        'conductivity' => 'decimal:4',
        'dignity_score' => 'decimal:4',
    ];

    public function article()
    {
        return $this->belongsTo(Article::class);
    }

    public function evidences()
    {
        return $this->hasMany(Evidence::class);
    }

    public function evidenceChains()
    {
        return $this->hasMany(EvidenceChain::class);
    }
}
