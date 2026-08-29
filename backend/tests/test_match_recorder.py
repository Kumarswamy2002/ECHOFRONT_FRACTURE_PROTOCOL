from backend.app.replay.match_recorder import MatchReplayRecorder

def test_replay_recording():
    rec = MatchReplayRecorder("match-007")
    rec.record_frame(1, {"p1": (0,0)})
    rec.record_key_event(10, "KILL", {"killer": "p1", "victim": "p2"})
    summary = rec.export_summary()
    assert summary["total_frames"] == 1
    assert summary["key_events_count"] == 1
