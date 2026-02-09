<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class EvidenceChain extends Model
{
    use HasFactory;

    protected $fillable = [
        'fact_check_id',
        'step_name',
        'input_content',
        'output_content',
        'score'
    ];

    protected $casts = [
        'score' => 'decimal:4',
    ];

    public function factCheck()
    {
        return $this->belongsTo(FactCheck::class);
    }
}
