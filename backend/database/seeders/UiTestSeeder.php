<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use Carbon\Carbon;

class UiTestSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // 1. Clean up existing test data
        // DB::table('articles')->where('title', 'SAP RESTful ABAP Programming Model (RAP)')->delete();

        // 2. Create Article
        $articleId = Str::uuid()->toString();
        $now = Carbon::now();

        // NOTE: Use DOUBLE QUOTES for \n to be interpreted as newline!
        $content = "# Overview\n" .
            "The SAP RESTful ABAP Programming Model (RAP) determines the architecture for efficient end-to-end development of intrinsically SAP HANA-optimized OData services (such as Fiori apps) in SAP BTP ABAP Environment and SAP S/4HANA.\n\n" .
            "## Key Features\n" .
            "*   **CDS-based Modeling**: Uses Core Data Services (CDS) for data modeling and behavior definition.\n" .
            "*   **Behavior Definition & Implementation**: Defines transactional behavior (create, update, delete) in Behavior Definition Language (BDL).\n" .
            "*   **Service Binding & Definition**: Exposes data models as OData services.\n\n" .
            "## Evolution\n" .
            "RAP is the evolutionary successor to the ABAP Programming Model for SAP Fiori, providing a standardized and efficient way to build enterprise-grade applications.";

        DB::table('articles')->insert([
            'id' => $articleId,
            'title' => 'SAP RESTful ABAP Programming Model (RAP)',
            'content' => $content,
            'module' => 'ABAP',
            'status' => 'published',
            'last_verified_at' => $now,
            'created_at' => $now,
            'updated_at' => $now,
        ]);

        // 3. Create Domain Ratings
        $domains = [
            ['domain' => 'help.sap.com', 'pc1_score' => 0.9500, 'category' => 'Official'],
            ['domain' => 'blogs.sap.com', 'pc1_score' => 0.6500, 'category' => 'Community'],
            ['domain' => 'developers.sap.com', 'pc1_score' => 0.9000, 'category' => 'Official'],
        ];

        foreach ($domains as $d) {
            DB::table('domain_ratings')->updateOrInsert(
                ['domain' => $d['domain']],
                ['pc1_score' => $d['pc1_score'], 'category' => $d['category'], 'updated_at' => $now]
            );
        }

        // 4. Create Fact Check
        $synthContent = "# Overview\n" .
            "The **SAP RESTful ABAP Programming Model (RAP)** is the strategic architecture for developing cloud-ready applications on **SAP BTP ABAP Environment** and **SAP S/4HANA**[1]. It is designed to efficiently build OData services and Fiori applications that are optimized for SAP HANA[1].\n\n" .
            "## Key Components\n" .
            "RAP relies on three main pillars:\n" .
            "1.  **Core Data Services (CDS)**: Used for the data model and structural definition[2].\n" .
            "2.  **Behavior Definition/Implementation**: Defines the transactional behavior using the Behavior Definition Language (BDL) and ABAP implementation classes[3].\n" .
            "3.  **Service Exposition**: Services are exposed via Service Definitions and Service Bindings[1].\n\n" .
            "## Evolution and Strategy\n" .
            "RAP is officially positioned as the evolutionary successor to the **ABAP Programming Model for SAP Fiori**[2]. It unifies the programming model for both brownfield (existing code) and greenfield development scenarios on the ABAP platform.";

        $factCheckId = DB::table('fact_checks')->insertGetId([
            'article_id' => $articleId,
            'status' => 'verified',
            'assertion_text' => 'RAP uses CDS for modeling, BDL for behavior, and is the successor to the ABAP Programming Model for SAP Fiori.',
            'synthesized_text' => $synthContent,
            'nlc_score' => 0.9800,
            'evidence_count' => 3,
            'last_checked_at' => $now,
            'created_at' => $now,
            'updated_at' => $now,
        ]);

        // 5. Create Evidences
        $evidences = [
            [
                'fact_check_id' => $factCheckId,
                'reference_num' => 1,
                'url' => 'https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/2d416a27b354101488c005f72671c667.html',
                'title' => 'SAP RESTful ABAP Programming Model - SAP Help Portal',
                'quote' => 'The SAP RESTful ABAP Programming Model (RAP) defines the architecture for efficient end-to-end development of intrinsically SAP HANA-optimized OData services (such as Fiori apps) in SAP BTP ABAP Environment and SAP S/4HANA.',
                'snippet' => 'Official documentation describing RAP architecture and its availability on BTP and S/4HANA.',
                'pc1_score' => 0.9500,
                'is_primary' => true,
            ],
            [
                'fact_check_id' => $factCheckId,
                'reference_num' => 2,
                'url' => 'https://blogs.sap.com/2019/10/25/getting-started-with-the-abap-restful-programming-model/',
                'title' => 'Getting Started with RAP - SAP Community Blogs',
                'quote' => 'RAP is the evolutionary successor to the ABAP Programming Model for SAP Fiori. It uses CDS for data modeling and is intended for all types of Fiori applications.',
                'snippet' => 'Blog post by Andre Fischer explaining the evolution from the previous model to RAP.',
                'pc1_score' => 0.6500,
                'is_primary' => false,
            ],
            [
                'fact_check_id' => $factCheckId,
                'reference_num' => 3,
                'url' => 'https://developers.sap.com/tutorials/abap-environment-restful-programming-model.html',
                'title' => 'Create Your First RAP Service',
                'quote' => 'You define the transactional behavior of your business object in the behavior definition... and implement it in the behavior implementation class.',
                'snippet' => 'Tutorial showing how to define behavior using BDL.',
                'pc1_score' => 0.9000,
                'is_primary' => true,
            ],
        ];

        foreach ($evidences as $ev) {
            DB::table('evidences')->insert(array_merge($ev, ['created_at' => $now, 'updated_at' => $now]));
        }

        // 6. Create Article References (Footer list)
        $refData = [
            [
                'id' => Str::uuid()->toString(),
                'type' => 'official_doc',
                'url' => 'https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/2d416a27b354101488c005f72671c667.html',
                'title' => 'SAP RESTful ABAP Programming Model - SAP Help Portal',
                'created_at' => $now,
                'updated_at' => $now,
            ],
            [
                'id' => Str::uuid()->toString(),
                'type' => 'community_blog',
                'url' => 'https://blogs.sap.com/2019/10/25/getting-started-with-the-abap-restful-programming-model/',
                'title' => 'Getting Started with RAP - SAP Community Blogs',
                'created_at' => $now,
                'updated_at' => $now,
            ],
            [
                'id' => Str::uuid()->toString(),
                'type' => 'official_doc',
                'url' => 'https://developers.sap.com/tutorials/abap-environment-restful-programming-model.html',
                'title' => 'Create Your First RAP Service - SAP Developers',
                'created_at' => $now,
                'updated_at' => $now,
            ]
        ];

        foreach ($refData as $ref) {
            // Insert into references table
            DB::table('references')->insert($ref);

            // Link in pivot table
            DB::table('article_references')->insert([
                'article_id' => $articleId,
                'reference_id' => $ref['id'],
                'created_at' => $now,
                'updated_at' => $now,
            ]);
        }

        // 7. Create Revision Reports (History)
        $oldContent = str_replace('intrinsically SAP HANA-optimized', 'SAP HANA-optimized', $content); // Slightly different content

        DB::table('revision_reports')->insert([
            'id' => Str::uuid()->toString(),
            'article_id' => $articleId,
            'creator_type' => 'human',
            'reason' => 'Fixed terminology regarding HANA optimization.',
            'before_content' => $oldContent,
            'after_content' => $content, // The current content
            'status' => 'approved',
            'processed_at' => $now->copy()->subDays(1),
            'created_at' => $now->copy()->subDays(2),
            'updated_at' => $now->copy()->subDays(1),
        ]);

        // Pending AI Proposal
        DB::table('revision_reports')->insert([
            'id' => Str::uuid()->toString(),
            'article_id' => $articleId,
            'creator_type' => 'ai',
            'reason' => 'Proposed update based on new SAP documentation regarding RAP guidelines.',
            'before_content' => $content,
            'after_content' => $content . "\n\n## Future Outlook\nRAP will continue to evolve...",
            'status' => 'pending',
            'created_at' => $now,
            'updated_at' => $now,
        ]);
    }
}
