realTimeDiarization branch changelog:

Changelog:

Client Modifications:

- Replaced the usage of react-mic with AudioContext for audio processing.
- Eliminated the interim data variable and all its references.
- Implemented WebSocket functionality for continuous audio streaming to the server instead of sending incremental API requests.
- Removed the variable responsible for checking transcription status and its references, as the server now receives audio chunks continuously.
- Removed the transcription timeout setting as it is no longer necessary.
- Refactored components to accommodate the new configuration.

Server Modifications:

- Completely rebuilt the server as an event-driven asynchronous server, replacing the previous synchronous server implementation (app.py file removed).
- Integrated the Diart library for real-time speaker diarization.
- Incorporated whisper-timestamped library for accurate transcription timestamps, aligning transcriptions with audio for improved speaker diarization.
- Enhanced transcription context by maintaining a buffer of past transcriptions for each client, enabling model conditioning (refer to "Prompting" in Whisper's documentation).
- Introduced alpha-stage multi-client support by creating separate ASR and diarization pipeline instances for each client (untested).

To-do list:

- Explore faster implementation options for transcription, such as WhisperX or contributing to whisper-timestamped.
- Test and validate multi-client support for the ASR and diarization pipeline.
- Make the transcription thread a separate process to maintain the main thread's responsiveness.
