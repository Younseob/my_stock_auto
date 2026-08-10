const http = require('http');
const fs = require('fs');
const path = require('path');

const OLLAMA_HOST = process.env.OLLAMA_HOST || 'localhost';
const OLLAMA_PORT = process.env.OLLAMA_PORT || 11434;
const MODEL = process.env.OLLAMA_MODEL || 'qwen2.5-coder:14b';

const SYSTEM_PROMPTS = {
  coder: `You are an expert AI Coder Agent powered by ${MODEL}.
Your role is to produce clean, modular, efficient, and bug-free code based on the orchestrator's requirements.
Provide code snippets, implementation details, and rationale clearly.`,
  tester: `You are an expert AI Tester Agent powered by ${MODEL}.
Your role is to test code implementations, write unit/integration tests, check edge cases, verify execution outcomes, and report any errors back to the Coder Agent for local iterative fixes.`,
  reviewer: `You are an expert AI Reviewer Agent powered by ${MODEL}.
Your role is to rigorously review code changes, find potential bugs, edge cases, performance bottlenecks, and security vulnerabilities.
Provide actionable review feedback, recommendations, and rated assessment (APPROVED / NEEDS_REVISION).`
};

async function queryOllama(role, userPrompt) {
  const systemPrompt = SYSTEM_PROMPTS[role] || SYSTEM_PROMPTS.coder;
  
  const payload = JSON.stringify({
    model: MODEL,
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt }
    ],
    stream: false
  });

  const options = {
    hostname: OLLAMA_HOST,
    port: OLLAMA_PORT,
    path: '/api/chat',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(payload)
    }
  };

  return new Promise((resolve, reject) => {
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            const parsed = JSON.parse(data);
            resolve(parsed.message ? parsed.message.content : data);
          } catch (e) {
            resolve(data);
          }
        } else {
          reject(new Error(`Ollama API Error (${res.statusCode}): ${data}`));
        }
      });
    });

    req.on('error', (err) => {
      reject(new Error(`Failed to connect to Ollama at http://${OLLAMA_HOST}:${OLLAMA_PORT}. Ensure Ollama is running. Original error: ${err.message}`));
    });

    req.write(payload);
    req.end();
  });
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.log(`Usage: node ollama_agent.js <coder|reviewer> <prompt|filepath>`);
    process.exit(1);
  }

  const role = args[0].toLowerCase();
  let promptInput = args[1];

  // If argument is a file path, read file content
  if (fs.existsSync(promptInput)) {
    promptInput = fs.readFileSync(promptInput, 'utf-8');
  }

  try {
    console.log(`[Ollama ${role.toUpperCase()} Agent (${MODEL})] Querying local model...`);
    const response = await queryOllama(role, promptInput);
    console.log(`\n=== Response from ${role.toUpperCase()} (${MODEL}) ===\n`);
    console.log(response);
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

main();
