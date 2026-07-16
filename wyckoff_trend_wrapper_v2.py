import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, 'src'))

try:
    from wyckoff_parser import WyckoffCockpitFormatter
except ImportError:
    print("FATAL: wyckoff_parser.py not found in src/.")
    sys.exit(1)

class WyckoffTrendWrapper:
    def __init__(self):
        self.formatter = WyckoffCockpitFormatter("config/wyckoff_event_tags.json")
        
    def process_tape_event(self, asset, phase_text, event_sequence, current_event, context_note):
        summary_line = self.formatter.render_asset_summary(
            asset, phase_text, event_sequence, current_event
        )
        
        detail_block = self.formatter.render_detail_block(
            asset, phase_text, event_sequence, current_event, context_note
        )
        
        action_tag = self.formatter.tags.get(current_event, {}).get("action_tag", "OBSERVE_ONLY")
        
        return {
            "asset": asset,
            "action_tag": action_tag,
            "cockpit_summary": summary_line,
            "cockpit_detail": detail_block
        }
