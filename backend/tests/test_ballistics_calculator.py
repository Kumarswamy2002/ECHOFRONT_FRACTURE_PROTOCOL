from backend.app.loadout.ballistics_calculator import WeaponBallisticsCalculator

def test_attachment_modification():
    base = {"recoil": 50.0, "ads_speed_ms": 250.0, "velocity_mps": 700.0}
    mods = [{"recoil": -10.0, "ads_speed_ms": 20.0}, {"velocity_mps": 50.0}]
    res = WeaponBallisticsCalculator.calculate_modified_stats(base, mods)
    assert res["recoil"] == 40.0
    assert res["velocity_mps"] == 750.0
