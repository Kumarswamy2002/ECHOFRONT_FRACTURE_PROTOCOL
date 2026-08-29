from backend.app.comms.tactical_radio import TacticalRadioProtocol

def test_radio_signal_strength():
    strength = TacticalRadioProtocol.calculate_signal_strength((0,0), (10,0))
    assert 0.0 <= strength <= 1.0
