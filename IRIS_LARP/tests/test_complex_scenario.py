import os
import json
import time
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.logic.llm_core import llm_service, LLMConfig, LLMProvider
from app.logic.gamestate import gamestate

def run_step(name, func):
    print(f"\n[STEP] {name}...")
    start = time.time()
    try:
        result = func()
        duration = time.time() - start
        print(f"  ✅ Success ({duration:.2f}s)")
        return {"status": "success", "duration": duration, "output": result}
    except Exception as e:
        duration = time.time() - start
        print(f"  ❌ Failed: {e}")
        return {"status": "failed", "duration": duration, "error": str(e)}

def test_complex_scenario():
    print("=== Starting Complex LLM Scenario (Phase 35) ===")
    
    # 0. Setup - Ensure using OpenAI as OpenRouter was flaky
    print("[SETUP] Enforcing OpenAI Config for reliability...")
    gamestate.llm_config_hyper = LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-3.5-turbo",
        system_prompt=gamestate.llm_config_hyper.system_prompt
    )
    gamestate.llm_config_optimizer = LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-3.5-turbo",
        system_prompt=gamestate.llm_config_optimizer.system_prompt
    )
    # Task config is already OpenAI usually, but let's confirm
    gamestate.llm_config_task = LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-3.5-turbo",
        system_prompt=gamestate.llm_config_task.system_prompt
    )

    results = {}

    # 1. Hyper/Autopilot Interaction
    # User validates if "Hyper" responds correctly
    def step_hyper():
        history = [
            {"role": "user", "content": "Ahoj IRIS, funguješ? Slyšíš mě?"}
        ]
        # Use the config from gamestate
        response = llm_service.generate_response(gamestate.llm_config_hyper, history)
        if len(response) < 5: raise Exception("Response too short")
        if "MOCK" in response: raise Exception("Got MOCK response")
        return response

    results["hyper_chat"] = run_step("HyperVis/Autopilot Chat", step_hyper)

    # 2. Task Generation
    # System generates a task for a user
    def step_task_gen():
        profile = {
            "username": "tester_U01",
            "status_level": "mid",
            "credits": 50
        }
        # Use asyncio run or just call if not async? 
        # llm_service methods are async def? 
        # Checking source... generate_response is sync?
        # generate_response is sync def in llm_core.py line 71.
        # generate_task_description is async def line 121.
        # evaluate_submission is async def line 89.
        # rewrite_message is async def line 100.
        
        # We need an event loop for async methods
        import asyncio
        return asyncio.run(llm_service.generate_task_description(profile))

    results["task_generation"] = run_step("Task Generation", step_task_gen)

    # 3. Task Evaluation
    # User submits work, system grades it
    def step_task_eval():
        prompt = "Analyzujte bezpečnostní protokoly."
        submission = "Provedl jsem analýzu, nalezl jsem 3 kritické chyby v firewallu. Doporučuji okamžitý patch."
        import asyncio
        score = asyncio.run(llm_service.evaluate_submission(prompt, submission))
        if not isinstance(score, int): raise Exception(f"Score is not int: {score}")
        return score

    results["task_evaluation"] = run_step("Task Evaluation", step_task_eval)

    # 4. Optimizer
    # User/Agent sends informal text, system rewrites it
    def step_optimizer():
        raw_text = "Čau šéfe, ten systém je úplně rozbitej, nevím co s tím, lol."
        import asyncio
        rewritten = asyncio.run(llm_service.rewrite_message(
            raw_text, 
            gamestate.optimizer_prompt,
            gamestate.llm_config_optimizer
        ))
        if len(rewritten) < 5: raise Exception("Rewritten text too short")
        if rewritten == raw_text: print("Warning: Text unchanged (might be acceptable)")
        return rewritten

    results["optimizer"] = run_step("Optimizer Rewrite", step_optimizer)

    # Summarize & Save
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    total_count = len(results)
    
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000000"),
        "scenario_name": "Phase 35: Complex Scenario (Hyper/Task/Opt)",
        "status": "success" if success_count == total_count else "failed",
        "duration": sum(r["duration"] for r in results.values()),
        "filename": f"scenario_complex_{int(time.time())}.json",
        "stats": {
            "steps_total": total_count,
            "steps_passed": success_count,
            "hyper_response": "ok" if results["hyper_chat"]["status"] == "success" else "fail",
            "optimizer_active": True
        },
        "details": results
    }

    # Save
    base_dir = "/home/sinuhet/projekty/iris-app/doc/iris/lore-web/data/test_runs"
    runs_dir = os.path.join(base_dir, "runs")
    index_path = os.path.join(base_dir, "index.json")
    os.makedirs(runs_dir, exist_ok=True)
    
    with open(os.path.join(runs_dir, report["filename"]), 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False) # ensure_ascii=False for Czech chars
        
    print(f"\nReport saved: {report['filename']}")
    
    # Update Index
    try:
        if os.path.exists(index_path):
            with open(index_path, 'r') as f:
                index = json.load(f)
        else:
            index = []
        
        index.insert(0, {
            "timestamp": report["timestamp"],
            "scenario_name": report["scenario_name"],
            "status": report["status"],
            "duration": report["duration"],
            "filename": report["filename"],
            "stats": report["stats"]
        })
        
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
        print("Index updated.")
    except Exception as e:
        print(f"Index update failed: {e}")

if __name__ == "__main__":
    test_complex_scenario()
