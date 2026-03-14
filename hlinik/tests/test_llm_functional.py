import os
import json
import time
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.logic.llm_core import LLMService, LLMConfig, LLMProvider

# Load env from IRIS_LARP/.env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def test_llm_generation_functional():
    print(f"\n--- Starting LLM Functional Test ---")
    service = LLMService()
    
    # Use OpenRouter as it seems to be the default preference in config
    # Try a known reliable model from previous successful runs or default
    model_name = "gpt-3.5-turbo"
    
    config = LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name=model_name,
        system_prompt="You are IRIS, a futuristic AI system. Answer deeply and mysteriously."
    )
    
    prompt = "Analyze the stability of the HLINIK protocol."
    print(f"Sending Prompt: '{prompt}' to {model_name}...")
    
    start_time = time.time()
    try:
        response = service.generate_response(config, [{"role": "user", "content": prompt}])
    except Exception as e:
        raise Exception(f"LLM Generation failed: {e}")
        
    duration = time.time() - start_time
    print(f"Response ({duration:.2f}s): {response}")
    
    # Validation
    assert response is not None
    assert len(response) > 10, "Response too short"
    assert "MOCK" not in response, "Got MOCK response, keys might be missing or invalid"
    
    # Generate Report Structure for Lore Web
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000000"),
        "scenario_name": "Phase 35: LLM Functional Test",
        "status": "success",
        "duration": float(f"{duration:.2f}"),
        "filename": f"llm_func_{int(start_time)}.json",
        "stats": {
            "provider": "OPENAI",
            "model": model_name,
            "prompt_len": len(prompt),
            "response_len": len(response),
            "sanity_check": "passed"
        },
        "details": {
            "prompt": prompt,
            "response_full": response,
            "config": config.dict()
        }
    }
    
    # Paths
    base_dir = "/home/sinuhet/projekty/iris-app/doc/iris/lore-web/data/test_runs"
    runs_dir = os.path.join(base_dir, "runs")
    index_path = os.path.join(base_dir, "index.json")
    
    os.makedirs(runs_dir, exist_ok=True)
    
    # Save Run JSON
    run_file_path = os.path.join(runs_dir, report['filename'])
    with open(run_file_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Report saved to: {run_file_path}")
    
    # Update Index JSON
    try:
        if os.path.exists(index_path):
            with open(index_path, 'r') as f:
                index = json.load(f)
        else:
            index = []
            
        index_entry = {
            "timestamp": report["timestamp"],
            "scenario_name": report["scenario_name"],
            "status": report["status"],
            "duration": report["duration"],
            "filename": report["filename"],
            "stats": report["stats"]
        }
        
        index.insert(0, index_entry)
        
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
        print("Index updated successfully.")
            
    except Exception as e:
        print(f"Warning: Could not update index.json: {e}")

if __name__ == "__main__":
    test_llm_generation_functional()
