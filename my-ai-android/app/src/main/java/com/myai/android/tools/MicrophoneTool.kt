package com.myai.android.tools

import android.content.Context
import android.media.AudioRecord
import android.media.MediaRecorder

class MicrophoneTool : ToolExecutor {
    override val toolName = "microphone"
    private var recorder: AudioRecord? = null
    private var recording = false

    override suspend fun execute(action: String, params: Map<String, String>, context: Context): ToolResult {
        return try {
            when (action) {
                "status" -> ToolResult(true, "Recording: ${if (recording) "ACTIVE" else "IDLE"}")
                "stop" -> {
                    recorder?.stop(); recorder?.release(); recorder = null; recording = false
                    ToolResult(true, "Stopped")
                }
                else -> ToolResult(false, error = "Use status/stop")
            }
        } catch (e: Exception) { ToolResult(false, error = e.message) }
    }
}
