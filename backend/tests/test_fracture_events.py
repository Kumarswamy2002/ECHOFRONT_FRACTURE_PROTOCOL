from backend.app.zones.fracture_events import FractureEventManager

def test_spawn_anomaly():
    res = FractureEventManager.spawn_anomaly("zone-alpha", "EMP_SURGE", 4)
    assert res["status"] == "ACTIVE"
    assert res["radiation_radius_meters"] == 100.0
