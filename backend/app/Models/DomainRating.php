<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class DomainRating extends Model
{
    use HasFactory;

    protected $fillable = [
        'domain',
        'pc1_score',
        'category'
    ];

    protected $casts = [
        'pc1_score' => 'decimal:4',
    ];
}
