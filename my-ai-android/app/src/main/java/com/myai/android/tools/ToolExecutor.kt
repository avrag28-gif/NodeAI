package com.myai.android.tools

import android.content.Context

interface ToolExecutor {
    val toolName: String
    suspend fun execute(action: String, params: Map<String, String>, context: Context): ToolResult
}

data class ToolResult(
    val success: Boolean,
    val data: String? = null,
    val error: String? = null
)
