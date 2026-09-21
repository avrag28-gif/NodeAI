package com.myai.android.data.model

data class ToolRequest(
    val tool: String,
    val action: String,
    val parameters: Map<String, String> = emptyMap()
)

data class ToolResponse(
    val success: Boolean,
    val result: String? = null,
    val error: String? = null
)
