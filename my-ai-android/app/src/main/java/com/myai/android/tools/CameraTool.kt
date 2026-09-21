package com.myai.android.tools

import android.content.Context
import android.hardware.camera2.CameraManager

class CameraTool : ToolExecutor {
    override val toolName = "camera"

    override suspend fun execute(action: String, params: Map<String, String>, context: Context): ToolResult {
        return try {
            val cm = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
            when (action) {
                "info" -> {
                    val cameras = cm.cameraIdList.joinToString("\n") { "  Camera $it" }
                    ToolResult(true, "Cameras (${cm.cameraIdList.size}):\n$cameras")
                }
                else -> ToolResult(false, error = "Use info")
            }
        } catch (e: Exception) { ToolResult(false, error = e.message) }
    }
}
