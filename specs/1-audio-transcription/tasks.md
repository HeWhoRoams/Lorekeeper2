# Tasks: audio-transcription

**Input**: Design documents from `/specs/1-audio-transcription/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No tests explicitly requested in feature specification - focusing on implementation tasks only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md: Single project with transcription module in `src/transcription/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for transcription module

- [x] T001 Create src/transcription/ directory structure
- [x] T002 Add whisperx and torch dependencies to requirements.txt
- [x] T003 [P] Create src/transcription/__init__.py module marker

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core transcription infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create TranscriptSegment model in src/models/transcript_segment.py
- [x] T005 Create TranscriptionLog model in src/models/transcription_log.py
- [x] T006 Create transcription service base class in src/transcription/transcription_service.py
- [x] T007 Setup async processing infrastructure with ThreadPoolExecutor in src/transcription/async_processor.py
- [x] T008 Configure WhisperX model loading with GPU/CPU fallback in src/transcription/model_manager.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Audio Transcription (Priority: P1) 🎯 MVP

**Goal**: Load recorded audio file and metadata, run WhisperX transcription, save timestamped transcript with word-level alignment

**Independent Test**: Provide valid session_audio_16k.wav and metadata.json files, verify transcript.json is created with accurate timestamps and text

### Implementation for User Story 1

- [x] T009 [US1] Implement audio file loading in src/transcription/audio_loader.py
- [x] T010 [US1] Implement metadata parsing in src/transcription/metadata_parser.py
- [x] T011 [US1] Implement WhisperX transcription runner in src/transcription/whisper_runner.py
- [x] T012 [US1] Implement transcript JSON output writer in src/transcription/transcript_writer.py
- [x] T013 [US1] Integrate components in transcription service transcribe method
- [x] T014 [US1] Add transcription logging with runtime and model metrics

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Speaker Diarization (Priority: P2)

**Goal**: When diarization is enabled, identify different speakers and assign consistent labels to transcript segments

**Independent Test**: Record multi-speaker audio, enable diarization, verify speaker labels are assigned consistently

### Implementation for User Story 2

- [x] T015 [US2] Add pyannote.audio dependency to requirements.txt
- [x] T016 [US2] Implement speaker diarization service in src/transcription/diarization_service.py
- [x] T017 [US2] Integrate diarization with WhisperX alignment in src/transcription/diarization_runner.py
- [x] T018 [US2] Update transcript writer to include speaker labels in output
- [x] T019 [US2] Add diarization configuration options to transcription service

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Asynchronous Processing (Priority: P3)

**Goal**: Run transcription in background without blocking Discord bot's main loop

**Independent Test**: Start transcription, verify bot can still respond to commands during processing

### Implementation for User Story 3

 - [X] T020 [US3] Create async transcription job manager in src/transcription/job_manager.py
 - [X] T021 [US3] Implement background task queuing in src/transcription/task_queue.py
 - [X] T022 [US3] Add async transcription endpoint to main bot in main.py
 - [X] T023 [US3] Integrate job status checking in bot commands
 - [X] T024 [US3] Add transcription completion notifications

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

 - [X] T025 [P] Add comprehensive error handling across all transcription components
 - [X] T026 [P] Implement transcript JSON schema validation in src/transcription/validator.py
 - [X] T027 Update main.py to integrate transcription service with existing bot commands
 - [X] T028 Add transcription configuration management in src/config/transcription_config.py
- [X] T029 Update README.md with transcription capabilities and usage examples
- [X] T030 Run quickstart.md validation scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but independently testable

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch foundational models together:
Task: "Create TranscriptSegment model in src/models/transcript_segment.py"
Task: "Create TranscriptionLog model in src/models/transcription_log.py"

# Launch core US1 components together:
Task: "Implement audio file loading in src/transcription/audio_loader.py"
Task: "Implement metadata parsing in src/transcription/metadata_parser.py"
Task: "Implement WhisperX transcription runner in src/transcription/whisper_runner.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence