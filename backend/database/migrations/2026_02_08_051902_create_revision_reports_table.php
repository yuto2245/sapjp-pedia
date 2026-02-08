<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('revision_reports', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->uuid('article_id');
            $table->foreign('article_id')->references('id')->on('articles')->onDelete('cascade');
            $table->enum('creator_type', ['human', 'ai']);
            $table->text('reason');
            $table->longText('before_content');
            $table->longText('after_content');
            $table->enum('status', ['pending', 'approved', 'rejected'])->default('pending');
            $table->json('reference_ids')->nullable();
            $table->timestamp('processed_at')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('revision_reports');
    }
};
