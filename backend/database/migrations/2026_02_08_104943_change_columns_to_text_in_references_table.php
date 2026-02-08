<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        // MySQL/MariaDB specific raw SQL
        DB::statement('ALTER TABLE `references` MODIFY `url` TEXT NULL');
        DB::statement('ALTER TABLE `references` MODIFY `title` TEXT NOT NULL');
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        DB::statement('ALTER TABLE `references` MODIFY `url` VARCHAR(255) NULL');
        DB::statement('ALTER TABLE `references` MODIFY `title` VARCHAR(255) NOT NULL');
    }
};
