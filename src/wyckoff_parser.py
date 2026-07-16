import json
import os

class WyckoffCockpitFormatter:
    def __init__(self, config_path="config/wyckoff_event_tags.json"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base_dir, config_path)

        try:
            with open(full_path, 'r') as f:
                self.tags = json.load(f)
        except Exception as e:
            self.tags = {}
            print(f"Warning: Could not load Wyckoff config: {e}")

        self.seen_acronyms = set()

    def _format_acronym(self, acronym):
        if acronym not in self.tags:
            return acronym
        event_name = self.tags[acronym].get("event_name", "")
        if acronym in self.seen_acronyms:
            return acronym
        else:
            self.seen_acronyms.add(acronym)
            return f"{acronym} ({event_name})"

    def render_asset_summary(self, asset, phase_text, event_sequence, current_event):
        if current_event not in self.tags:
            return f"{asset}: {phase_text}, {current_event} -> UNKNOWN_EVENT"
        action_tag = self.tags[current_event].get("action_tag", "UNKNOWN")
        formatted_sequence = " -> ".join([self._format_acronym(e.strip()) for e in event_sequence.split("->")])
        return f"{asset}: {phase_text}, {formatted_sequence} -> {action_tag}"

    def render_detail_block(self, asset, phase_text, event_sequence, current_event, context_note):
        if current_event not in self.tags:
            return f"=== {asset} Structure ===\nError: Unknown event {current_event}"
        data = self.tags[current_event]
        action_tag = data.get("action_tag", "UNKNOWN")
        allowed = "; ".join(data.get("allowed_actions", []))
        risk = data.get("risk_posture", "unknown")
        formatted_sequence = " -> ".join([self._format_acronym(e.strip()) for e in event_sequence.split("->")])
        formatted_current = self._format_acronym(current_event)
        out = f"=== {asset} Structure ===\n"
        out += f"structure_phase: {phase_text}\n"
        out += f"event_sequence: {formatted_sequence}\n"
        out += f"event: {formatted_current}\n"
        out += f"context_note: {context_note}\n"
        out += f"deployment_bias: {action_tag} - {allowed}\n"
        out += f"risk_frame: {risk} posture\n"
        return out

if __name__ == "__main__":
    formatter = WyckoffCockpitFormatter()
    print("--- AUTO Mode Summary Test ---")
    print(formatter.render_asset_summary("XLM", "Phase D accumulation", "SOS -> BUEC -> LPS", "LPS"))
    print("\n--- Detail Block Test ---")
    formatter.seen_acronyms.clear()
    print(formatter.render_detail_block(
        "XLM",
        "ACCUMULATION Phase D",
        "SOS -> BUEC -> LPS",
        "LPS",
        "Price jumped across prior resistance and is retesting."
    ))
