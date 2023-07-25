Changelog:

Client Modifications:

- Replaced the usage of `react-mic` with `AudioContext` for audio processing, improving audio quality and performance.
- Eliminated the interim data variable and all its references, leading to a more efficient and cleaner codebase.
- Implemented WebSocket functionality for continuous audio streaming to the server, significantly reducing latency and improving real-time transcription capabilities.
- Removed the variable responsible for checking transcription status and its references, as the server now seamlessly receives audio chunks.
- Removed the transcription timeout setting as it is no longer necessary due to continuous audio streaming.
- Refactored components to accommodate the new configuration, making the client-side implementation more maintainable.

Server Modifications:

- Completely rebuilt the server as an event-driven asynchronous server, replacing the previous synchronous server implementation (app.py file removed). This change brings scalability and performance improvements.
- Integrated the Diart library for real-time speaker diarization, allowing for the identification of different speakers during transcription.
- Incorporated the whisper-timestamped library for accurate transcription timestamps, aligning transcriptions with audio for improved speaker diarization and transcript precision.
- Enhanced transcription context by maintaining a buffer of past transcriptions for each client, enabling model conditioning through Whisper's "Prompting" feature.
- The stream now transcribes data in batches, optimizing the transcription process for better efficiency and speed.
- Implemented efficient handling of sudden disconnects and stream stoppings, ensuring all remaining audio data is transcribed and sent to the client before the connection shuts off.
- Detailed logging of the server's operations using Python's built-in logging library, facilitating debugging and monitoring.

Contribution Ideas:

- Explore faster implementation options for transcription, such as WhisperX, and conduct a thorough analysis of pros and cons between alignment models to evaluate potential performance gains.
- Add multi-client support to enable concurrent audio streaming and transcription for multiple users, making the system more versatile and accessible.
