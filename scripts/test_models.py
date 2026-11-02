import asyncio
import os
from dotenv import load_dotenv
from groq import AsyncGroq
from openai import AsyncOpenAI

load_dotenv(".env")


async def test_groq():
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("MODEL_ROUTER", "openai/gpt-oss-20b")
    print(f"\n=== Testing Groq Router: {model} ===")
    if not api_key:
        print("✗ ERROR: No GROQ_API_KEY found.")
        return False
    try:
        client = AsyncGroq(api_key=api_key)
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say hello in one sentence."}],
            max_completion_tokens=50,
            temperature=0.7,
        )
        content = resp.choices[0].message.content or "OK"
        print(f"[PASS] SUCCESS: {content[:100]}")
        return True
    except Exception as e:
        print(f"[FAIL] ERROR: {type(e).__name__}: {str(e)[:150]}")
        return False


async def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("MODEL_MODEL1", "gemini-3.5-flash-lite")
    print(f"\n=== Testing Gemini Deliberator: {model} ===")
    if not api_key:
        print("✗ ERROR: No GEMINI_API_KEY found.")
        return False
    try:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say hello in one sentence."}],
            max_completion_tokens=50,
            temperature=0.7,
        )
        content = resp.choices[0].message.content or ""
        print(f"[PASS] SUCCESS: {content[:100]}")
        return True
    except Exception as e:
        print(f"[FAIL] ERROR: {type(e).__name__}: {str(e)[:150]}")
        return False


async def main():
    print("Testing Hybrid AI endpoints (Groq + Gemini)...")
    result_groq = await test_groq()
    result_gemini = await test_gemini()

    print("\n=== Summary ===")
    print(f"Groq Triage: {'[PASS]' if result_groq else '[FAIL]'}")
    print(f"Gemini Deliberation: {'[PASS]' if result_gemini else '[FAIL]'}")

    if result_groq and result_gemini:
        print("\n[SUCCESS] Both providers working! Ready to run full council deliberation.")
    else:
        print("\nNotice: If one provider is unavailable, Consilium will automatically failover to the other.")


if __name__ == "__main__":
    asyncio.run(main())
