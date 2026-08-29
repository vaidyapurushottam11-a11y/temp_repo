from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Callable


class Stage(str, Enum):
    DISCOVER_TOPIC = "DISCOVER_TOPIC"
    RESEARCH = "RESEARCH"
    FACT_CHECK = "FACT_CHECK"
    WRITE_SCRIPT = "WRITE_SCRIPT"
    SCRIPT_QA = "SCRIPT_QA"
    TTS = "TTS"
    ALIGN = "ALIGN"
    STORYBOARD = "STORYBOARD"
    VISUALS = "VISUALS"
    VISUAL_QA = "VISUAL_QA"
    ASSEMBLE = "ASSEMBLE"
    VIDEO_QA = "VIDEO_QA"
    THUMBNAIL = "THUMBNAIL"
    METADATA = "METADATA"
    PUBLISH = "PUBLISH"


PIPELINE = list(Stage)


@dataclass
class EpisodeState:
    episode_id: str
    current_stage: str = Stage.DISCOVER_TOPIC.value
    status: str = "RUNNING"
    attempt: int = 0
    last_error: str | None = None


class StateStore:
    def __init__(self, root: Path = Path("state")) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, episode_id: str) -> Path:
        return self.root / f"{episode_id}.json"

    def load(self, episode_id: str) -> EpisodeState:
        path = self.path(episode_id)
        if not path.exists():
            return EpisodeState(episode_id=episode_id)
        return EpisodeState(**json.loads(path.read_text()))

    def save(self, state: EpisodeState) -> None:
        self.path(state.episode_id).write_text(json.dumps(asdict(state), indent=2))


class RecoverableStageError(RuntimeError):
    pass


class QuarantineStageError(RuntimeError):
    pass


def not_implemented(stage: Stage) -> Callable[[EpisodeState], None]:
    def runner(_: EpisodeState) -> None:
        raise RecoverableStageError(f"Provider/stage not configured yet: {stage.value}")
    return runner


class Orchestrator:
    def __init__(self, store: StateStore, max_attempts: int = 4) -> None:
        self.store = store
        self.max_attempts = max_attempts
        self.runners: dict[Stage, Callable[[EpisodeState], None]] = {
            stage: not_implemented(stage) for stage in PIPELINE
        }

    def register(self, stage: Stage, runner: Callable[[EpisodeState], None]) -> None:
        self.runners[stage] = runner

    def run(self, episode_id: str) -> EpisodeState:
        state = self.store.load(episode_id)
        start = PIPELINE.index(Stage(state.current_stage))

        for stage in PIPELINE[start:]:
            state.current_stage = stage.value
            state.attempt = 0
            state.last_error = None
            self.store.save(state)

            while state.attempt < self.max_attempts:
                try:
                    self.runners[stage](state)
                    break
                except RecoverableStageError as exc:
                    state.attempt += 1
                    state.last_error = str(exc)
                    self.store.save(state)
            else:
                state.status = "QUARANTINED"
                self.store.save(state)
                return state

            next_index = PIPELINE.index(stage) + 1
            if next_index < len(PIPELINE):
                state.current_stage = PIPELINE[next_index].value
                self.store.save(state)

        state.status = "PUBLISHED"
        self.store.save(state)
        return state
