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
        // 1. ドメイン格付けマスタ (PC1スコア)
        Schema::create('domain_ratings', function (Blueprint $table) {
            $table->id();
            $table->string('domain')->unique(); // help.sap.com
            $table->decimal('pc1_score', 5, 4)->default(0.5000); // 0.0000 - 1.0000
            $table->string('category')->nullable(); // Official, News, Blog
            $table->timestamps();
        });

        // 2. ファクトチェック結果
        Schema::create('fact_checks', function (Blueprint $table) {
            $table->id();
            $table->foreignUuid('article_id')->constrained()->onDelete('cascade');
            $table->string('status')->default('pending'); // verified, provisional, abstained, pending
            $table->text('assertion_text')->nullable(); // 検証対象の主張
            $table->text('synthesized_text')->nullable(); // 統合された回答文 (参照番号付き)
            $table->decimal('nlc_score', 5, 4)->nullable(); // No-Leap Constraint Score
            $table->decimal('conductivity', 5, 4)->nullable(); // 伝導率
            $table->decimal('dignity_score', 5, 4)->nullable(); // ディグニティ
            $table->integer('evidence_count')->default(0);
            $table->timestamp('last_checked_at')->nullable();
            $table->timestamps();
        });

        // 3. エビデンス (根拠)
        Schema::create('evidences', function (Blueprint $table) {
            $table->id();
            $table->foreignId('fact_check_id')->constrained()->onDelete('cascade');
            $table->integer('reference_num')->nullable(); // [1], [2]...
            $table->string('url', 1024);
            $table->string('title', 1024)->nullable();
            $table->text('quote')->nullable(); // 引用文
            $table->text('snippet')->nullable(); // 検索スニペット
            $table->decimal('pc1_score', 5, 4)->nullable(); // その時点でのPC1スコア
            $table->boolean('is_primary')->default(false);
            $table->string('status')->default('valid'); // valid, invalid
            $table->timestamps();
        });

        // 4. 思考プロセスログ (Evidence Chain)
        Schema::create('evidence_chains', function (Blueprint $table) {
            $table->id();
            $table->foreignId('fact_check_id')->constrained()->onDelete('cascade');
            $table->string('step_name'); // concept_extraction, bias_measurement, balance_generation
            $table->text('input_content')->nullable();
            $table->text('output_content')->nullable();
            $table->decimal('score', 5, 4)->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('evidence_chains');
        Schema::dropIfExists('evidences');
        Schema::dropIfExists('fact_checks');
        Schema::dropIfExists('domain_ratings');
    }
};
