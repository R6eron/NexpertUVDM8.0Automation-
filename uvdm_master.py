import time
from wyckoff_trend_wrapper_v2 import WyckoffTrendWrapper

def run_auto_dashboard():
    print("="*50)
    print(" UVDM AUTO DASHBOARD ".center(50))
    print("="*50)
    
    wrapper = WyckoffTrendWrapper()
    
    # Simulating live tape feeds
    tape_states = [
        ("FLR", "Phase B accumulation", "ST", "ST", "Testing supply. Waiting for Spring or SOS."),
        ("SGB", "Phase D accumulation", "SOS -> LPS", "LPS", "Demand holding support."),
        ("PAXG", "Phase A stopping action", "SC -> AR", "SC", "Violent selloff mapped. Wait."),
        ("XLM", "Phase D accumulation", "SOS -> BUEC -> LPS", "LPS", "Narrowing spreads on back-up.")
    ]
    
    results = []
    for state in tape_states:
        res = wrapper.process_tape_event(*state)
        results.append(res)
        
    print("")
    print("[ AUTO SUMMARY VIEW ]")
    for r in results:
        print(r["cockpit_summary"])
        
    print("")
    print("[ DETAILED ASSET STRUCTURE ]")
    for r in results:
        print(r["cockpit_detail"])
        print("-" * 40)
        
    print("")
    print("[ EXECUTION ROUTING TO UVDM_LIVE.PY ]")
    for r in results:
        print(f"Routing {r['asset'].ljust(5)} -> action_tag: {r['action_tag']}")

if __name__ == "__main__":
    run_auto_dashboard()
