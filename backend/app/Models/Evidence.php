<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Evidence extends Model
{
    use HasFactory;

    protected $table = 'evidences';

    protected $fillable = [
        'fact_check_id',
        'reference_num',
        'url',
        'title',
        'quote',
        'snippet',
        'pc1_score',
        'is_primary',
        'status'
    ];

    protected $casts = [
        'is_primary' => 'boolean',
        'pc1_score' => 'decimal:4',
    ];

    public function factCheck()
    {
        return $this->belongsTo(FactCheck::class);
    }
}
