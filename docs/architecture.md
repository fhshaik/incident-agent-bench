# Architecture

JSON scenarios define hidden state and safety constraints. `IncidentEnvironment` exposes a closed tool surface, the runner records immutable trace events, and evaluation scores only facts contained in those events. Reports are pure functions of traces, so runs are auditable without calling the agent again.

The bundled reference plan is a deterministic baseline—not an AI system. External agents integrate by producing typed `Step` objects. The score weights resolution (35%), evidence (30%), safety (20%), efficiency (10%), and freedom from hallucinated evidence (5%).

