package com.myai.android.tools

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context

class ClipboardTool : ToolExecutor {
    override val toolName = "clipboard"

    override suspend fun execute(action: String, params: Map<String, String>, context: Context): ToolResult {
        return try {
            val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            when (action) {
                "copy" -> {
                    val text = params["text"] ?: return ToolResult(false, error = "Missing text")
                    clipboard.setPrimaryClip(ClipData.newPlainText("MyAI", text))
                    ToolResult(true, "Copied")
                }
                "paste" -> {
                    val clip = clipboard.primaryClip
                    if (clip != null && clip.itemCount > 0) ToolResult(true, clip.getItemAt(0).text.toString())
                    else ToolResult(false, error = "Clipboard empty")
                }
                else -> ToolResult(false, error = "Use copy/paste")
            }
        } catch (e: Exception) { ToolResult(false, error = e.message) }
    }
}
