### Verifiable AI Workflow Notarization

A proof-of-concept system where AI agents perform data analysis, and their work is immutably recorded and verified on the Solana blockchain.

---

Using CrewAI, a team of autonomous agents processes documents, analyzes them with OpenAI or a local LLM (Ollama), and records cryptographic proofs of their work (input, output, environment hashes) on Solana.

### Current Capabilities

Sourcing Agent - Fetches authentic PDF reports, validates source, computes SHA-256 hash.
Analyst Agent - Parses PDFs, extracts key metrics, and generates LLM-based risk summaries.
Notarization Agent (in progress) - Prepares transaction data to record hashes and metadata on Solana devnet.
