/**
 * Publish 3 AceDataCloud tools for AtlasNexusScout on SAP mainnet.
 * 
 * ToolCategory enum: Swap=0, Lend=1, Stake=2, Nft=3, Payment=4, Data=5, Governance=6, Bridge=7, Analytics=8, Custom=9
 * ToolHttpMethod enum: Get=0, Post=1, Put=2, Delete=3, Compound=4
 * 
 * Usage: npx tsx publish-tools.ts --dry-run   (preview)
 *        npx tsx publish-tools.ts              (execute)
 */

import { createSapClient } from "@oobe-protocol-labs/synapse-sap-sdk";
import { Keypair, PublicKey, Transaction, sendAndConfirmTransaction } from "@solana/web3.js";
import * as anchor from "@coral-xyz/anchor";
import * as dotenv from "dotenv";
import bs58 from "bs58";
import { createHash } from "crypto";

dotenv.config();

const OOBE_API_KEY = process.env.OOBE_API_KEY!;
const PRIVATE_KEY = process.env.SOLANA_PRIVATE_KEY_BASE58!;
const AGENT_PDA = new PublicKey("FHTLFvsLijuvknHJSKwjfLGXFCV8a2X1cvMHJUEuTeer");
const RPC_URL = `https://us-1-mainnet.oobeprotocol.ai?api_key=${OOBE_API_KEY}`;

const ToolCategory = { Data: 5, Analytics: 8, Custom: 9 } as const;
const HttpMethod = { Post: 1 } as const;

function sha256(data: string): number[] {
  return Array.from(createHash("sha256").update(data).digest());
}

interface ToolDef {
  name: string;
  description: string;
  category: number;
  inputSchema: object;
  outputSchema: object;
  paramsCount: number;
  requiredParams: number;
}

const TOOLS: ToolDef[] = [
  {
    name: "acedatacloud-search",
    description: "Real-time web search via AceDataCloud — x402 payment required. Returns structured search results for crypto, DeFi, and market intelligence queries.",
    category: ToolCategory.Data,
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Search query" },
        max_results: { type: "number", default: 5 }
      },
      required: ["query"]
    },
    outputSchema: {
      type: "object",
      properties: { results: { type: "array" } }
    },
    paramsCount: 2,
    requiredParams: 1
  },
  {
    name: "acedatacloud-chat",
    description: "AI-powered intelligence analysis via AceDataCloud Chat (GPT-4o-mini). x402 micropayment per request. Delivers structured analysis with confidence scoring for crypto, DeFi, and market topics.",
    category: ToolCategory.Analytics,
    inputSchema: {
      type: "object",
      properties: {
        prompt: { type: "string", description: "Analysis prompt" },
        context: { type: "string", description: "Optional context data" }
      },
      required: ["prompt"]
    },
    outputSchema: {
      type: "object",
      properties: {
        analysis: { type: "string" },
        confidence: { type: "number" }
      }
    },
    paramsCount: 2,
    requiredParams: 1
  },
  {
    name: "acedatacloud-images",
    description: "AI image generation via AceDataCloud. x402 payment per generation. Creates visualizations, charts, and creative assets for data intelligence.",
    category: ToolCategory.Custom,
    inputSchema: {
      type: "object",
      properties: {
        prompt: { type: "string", description: "Image generation prompt" },
        style: { type: "string", default: "realistic" },
        size: { type: "string", default: "1024x1024" }
      },
      required: ["prompt"]
    },
    outputSchema: {
      type: "object",
      properties: {
        image_url: { type: "string" },
        generation_id: { type: "string" }
      }
    },
    paramsCount: 3,
    requiredParams: 1
  }
];

const DRY_RUN = process.argv.includes("--dry-run");

async function main() {
  if (!PRIVATE_KEY) throw new Error("SOLANA_PRIVATE_KEY_BASE58 not set in .env");
  if (!OOBE_API_KEY) throw new Error("OOBE_API_KEY not set in .env");

  const keypair = Keypair.fromSecretKey(bs58.decode(PRIVATE_KEY));
  const wallet = new anchor.Wallet(keypair);

  console.log(`🔮 AtlasNexusScout — Publishing ${TOOLS.length} tools`);
  console.log(`   Wallet: ${keypair.publicKey.toBase58()}`);
  console.log(`   Agent PDA: ${AGENT_PDA.toBase58()}`);
  if (DRY_RUN) console.log(`   ⚠️  DRY RUN — no transactions will be sent`);
  console.log("");

  const client = createSapClient(RPC_URL, wallet);

  // Global registry PDA (pre-initialized on SAP mainnet)
  const globalRegistryPda = new PublicKey("9odFrYBBZq6UQC6aGyzMPNXWJQn55kMtfigzhLg6S6L5");

  for (const tool of TOOLS) {
    console.log(`📦 Publishing: ${tool.name}...`);

    const inputSchemaStr = JSON.stringify(tool.inputSchema);
    const outputSchemaStr = JSON.stringify(tool.outputSchema);

    // Derive tool PDA — seeds: ["sap_tool", agent_pda, tool_name_hash]
    const [toolPda] = PublicKey.findProgramAddressSync(
      [Buffer.from("sap_tool"), AGENT_PDA.toBuffer(), Buffer.from(sha256(tool.name))],
      client.programId
    );

    console.log(`   Tool PDA: ${toolPda.toBase58()}`);
    console.log(`   Category: ${tool.category}, Method: POST`);

    if (DRY_RUN) {
      console.log(`   ⏭️  Skipped (dry-run)`);
      console.log("");
      continue;
    }

    try {
      const ix = await client.tools.publishTool({
        wallet: keypair.publicKey,
        agent: AGENT_PDA,
        tool: toolPda,
        globalRegistry: globalRegistryPda,
        signer: keypair,
        toolName: tool.name,
        toolNameHash: sha256(tool.name),
        protocolHash: sha256("x402"),
        descriptionHash: sha256(tool.description),
        inputSchemaHash: sha256(inputSchemaStr),
        outputSchemaHash: sha256(outputSchemaStr),
        httpMethod: HttpMethod.Post,
        category: tool.category,
        paramsCount: tool.paramsCount,
        requiredParams: tool.requiredParams,
        isCompound: false,
      });

      const { blockhash, lastValidBlockHeight } = await client.connection.getLatestBlockhash();
      const tx = new Transaction({ blockhash, lastValidBlockHeight, feePayer: keypair.publicKey }).add(ix);
      const sig = await sendAndConfirmTransaction(
        client.connection,
        tx,
        [keypair],
        { commitment: "confirmed" }
      );

      console.log(`   ✅ Published!`);
      console.log(`   Tx: https://solscan.io/tx/${sig}`);
      console.log("");
    } catch (err: any) {
      const msg = err.message || String(err);
      console.error(`   ❌ Failed: ${msg}`);
      if (err.logs) {
        console.error(`   Logs: ${err.logs.slice(-3).join(" | ")}`);
      }
      console.log("");
    }
  }

  console.log(`✅ ${DRY_RUN ? "Dry run complete" : "Done! View at https://explorer.oobeprotocol.ai/tools"}`);
}

main().catch(console.error);
