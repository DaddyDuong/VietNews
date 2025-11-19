# Detailed Input/Output Handling

Short: Shows function-level IO from reading bulletins to saving audio files.

```mermaid
graph LR
    A[bulletin_reader.read_bulletin()] --> B[audio_downloader.download_audio()]
    B --> C[file_manager.manage_files()]
```
