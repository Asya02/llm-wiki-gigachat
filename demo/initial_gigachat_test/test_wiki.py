"""Full LLM Wiki demo: ingest 4 sources, query, lint — with GigaChat via deepagents.

Designed to produce a rich wiki visible in Obsidian.
Traffic goes through mitmproxy if HTTP_PROXY/HTTPS_PROXY are set in .env.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

from langchain_gigachat import GigaChat

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

WORKSPACE = Path(__file__).resolve().parent
SOURCES_DIR = WORKSPACE / "sources"


def make_model() -> GigaChat:
    return GigaChat(
        model=os.getenv("GIGACHAT_MODEL", "GigaChat-3-Ultra"),
        base_url=os.getenv("GIGACHAT_BASE_URL", "https://gigachat.sberdevices.ru/v1"),
        verify_ssl_certs=os.getenv("GIGACHAT_VERIFY_SSL_CERTS", "False").lower() == "true",
        profanity_check=os.getenv("GIGACHAT_PROFANITY_CHECK", "False").lower() == "true",
        timeout=int(os.getenv("GIGACHAT_TIMEOUT", "180")),
    )


def make_agent():
    model = make_model()
    backend = FilesystemBackend(root_dir=str(WORKSPACE), virtual_mode=False)
    skill_path = WORKSPACE / "skills" / "karpathy-llm-wiki" / "SKILL.md"
    skill_text = skill_path.read_text()

    return create_deep_agent(
        model=model,
        system_prompt=skill_text,
        backend=backend,
        skills=["skills/"],
    )


def print_banner(label: str) -> None:
    print(f"\n{'='*72}")
    print(f"  {label}")
    print(f"{'='*72}")


def print_result(result: dict) -> None:
    for msg in result.get("messages", []):
        role = getattr(msg, "type", "unknown")
        content = getattr(msg, "content", "")
        if role == "ai" and content:
            print(f"\n[GigaChat]: {content}")
        elif role == "tool":
            name = getattr(msg, "name", "?")
            short = (content[:200] + "...") if len(content) > 200 else content
            print(f"  [{name}] {short}")


def run_step(label: str, user_message: str) -> dict:
    print_banner(label)
    print(f">>> {user_message[:120]}{'...' if len(user_message) > 120 else ''}\n")
    t0 = time.time()
    agent = make_agent()
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_message}]},
    )
    elapsed = time.time() - t0
    print_result(result)
    print(f"\n  ({elapsed:.1f}s)")
    return result


def main() -> None:
    proxy = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    print(f"Workspace : {WORKSPACE}")
    print(f"Model     : {os.getenv('GIGACHAT_MODEL', 'GigaChat-3-Ultra')}")
    print(f"Proxy     : {proxy or 'none (direct connection)'}")
    print()

    source_files = sorted(SOURCES_DIR.glob("*.md"))
    print(f"Sources to ingest: {len(source_files)}")
    for f in source_files:
        print(f"  - {f.name}")
    print()

    # --- Ingest all sources ---
    for i, src in enumerate(source_files, 1):
        text = src.read_text()
        run_step(
            f"INGEST {i}/{len(source_files)}: {src.stem}",
            f"Ingest the following source into the wiki.\n\n{text}",
        )

    # --- Query ---
    queries = [
        "What do I know about the Transformer architecture and its key innovations?",
        "Compare BERT and GPT — how do they differ in architecture and use cases?",
        "How does FlashAttention improve LLM training efficiency?",
    ]
    for i, q in enumerate(queries, 1):
        run_step(f"QUERY {i}/{len(queries)}", q)

    # --- Lint ---
    run_step("LINT", "Lint the wiki.")

    # --- Final state ---
    print_banner("FINAL STATE")
    for d in ("raw", "wiki"):
        p = WORKSPACE / d
        if p.exists():
            files = list(p.rglob("*.md"))
            print(f"\n{d}/ ({len(files)} files):")
            for f in sorted(files):
                print(f"  {f.relative_to(WORKSPACE)}")
        else:
            print(f"\n{d}/ — not created")

    print("\n\nOpen this folder in Obsidian to browse the wiki and see the graph view.")
    print(f"  Vault path: {WORKSPACE}")


if __name__ == "__main__":
    main()
