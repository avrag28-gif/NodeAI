package com.myai.android.tools

import android.content.Context
import android.hardware.camera2.CameraManager

class FlashlightTool : ToolExecutor {
    override val toolName = "flash"
    private var isOn = false

    override suspend fun execute(action: String, params: Map<String, String>, context: Context): ToolResult {
        return try {
            val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
            val cameraId = cameraManager.cameraIdList.firstOrNull()
                ?: return ToolResult(false, error = "No camera found")

            when (action) {
                "on" -> { cameraManager.setTorchMode(cameraId, true); isOn = true; ToolResult(true, "Flashlight ON") }
                "off" -> { cameraManager.setTorchMode(cameraId, false); isOn = false; ToolResult(true, "Flashlight OFF") }
                "toggle" -> { isOn = !isOn; cameraManager.setTorchMode(cameraId, isOn); ToolResult(true, "Flashlight ${if (isOn) "ON" else "OFF"}") }
                "status" -> ToolResult(true, "Flashlight is ${if (isOn) "ON" else "OFF"}")
                else -> ToolResult(false, error = "Use on/off/toggle/status")
            }
        } catch (e: Exception) { ToolResult(false, error = e.message) }
    }
}
