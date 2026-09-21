package com.myai.android.tools

import android.content.Context
import android.telephony.SmsManager

class SmsTool : ToolExecutor {
    override val toolName = "sms"

    override suspend fun execute(action: String, params: Map<String, String>, context: Context): ToolResult {
        return try {
            when (action) {
                "send" -> {
                    val phone = params["phone"] ?: return ToolResult(false, error = "Missing phone")
                    val msg = params["message"] ?: return ToolResult(false, error = "Missing message")
                    SmsManager.getDefault().sendTextMessage(phone, null, msg, null, null)
                    ToolResult(true, "SMS sent to $phone")
                }
                else -> ToolResult(false, error = "Use send")
            }
        } catch (e: Exception) { ToolResult(false, error = e.message) }
    }
}
