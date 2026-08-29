from backend.app.security.anti_cheat import AntiCheatAnalyzer

def test_anti_cheat_legit_and_speedhack():
    legit = AntiCheatAnalyzer.evaluate_movement_tick((0,0), (5,0), 1.0)
    assert legit["is_suspicious"] is False

    hack = AntiCheatAnalyzer.evaluate_movement_tick((0,0), (100,0), 1.0)
    assert hack["is_suspicious"] is True
    assert hack["violation_type"] == "SPEED_HACK"
