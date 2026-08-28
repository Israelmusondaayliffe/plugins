# Ownership and source boundaries

Loop Observatory owns cross-loop ingestion, normalization, portfolio metrics, and judge calibration. It does not design, execute, schedule, or repair an individual loop.

LoopKit is discovered only under `~/.codex/loopkit/` unless an explicit path is supplied. Operating Graph sources are read only from roots recorded by `register-root`. Source files are opened for reading and fingerprinting only.

`loopkit:loop-doctor`, `operating-graph:graph-debug`, and Agent Ops are optional repair destinations. If none is available, run `python3 ../scripts/loop_observatory.py repair-handoff RECORD_ID` and return its complete generic handoff. The handoff does not claim a repair. Missing acceptance, token, or cost evidence must remain unknown rather than being inferred.
