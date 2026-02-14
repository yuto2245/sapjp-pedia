<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\FactCheck;
use App\Models\Evidence;
use Illuminate\Support\Facades\DB;

class FactCheckController extends Controller
{
    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'article_id' => 'required|exists:articles,id',
            'status' => 'required|string|in:pending,verified,likely_correct,uncertain,likely_incorrect,refuted,abstained',
            'assertion_text' => 'nullable|string',
        ]);

        $factCheck = FactCheck::create($validated);

        return response()->json($factCheck, 201);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        $factCheck = FactCheck::findOrFail($id);

        $validated = $request->validate([
            'status' => 'sometimes|string|in:pending,verified,likely_correct,uncertain,likely_incorrect,refuted,abstained',
            'synthesized_text' => 'nullable|string',
            'nlc_score' => 'nullable|numeric',
            'conductivity' => 'nullable|numeric',
            'dignity_score' => 'nullable|numeric',
            'evidence_count' => 'sometimes|integer',
            'last_checked_at' => 'nullable|date',
        ]);

        $factCheck->update($validated);

        return response()->json($factCheck);
    }

    /**
     * Store evidences for a fact check.
     */
    public function storeEvidences(Request $request, string $id)
    {
        $factCheck = FactCheck::findOrFail($id);

        $validated = $request->validate([
            'evidences' => 'required|array',
            'evidences.*.url' => 'required|url',
            'evidences.*.quote' => 'nullable|string',
            'evidences.*.title' => 'nullable|string',
            'evidences.*.reference_num' => 'nullable|integer',
            'evidences.*.pc1_score' => 'nullable|numeric',
            'evidences.*.is_primary' => 'boolean',
        ]);

        $factCheck->evidences()->createMany($validated['evidences']);

        return response()->json(['message' => 'Evidences stored successfully'], 201);
    }
}
