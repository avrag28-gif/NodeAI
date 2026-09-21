package com.myai.android.data.model

data class ChatMessage(
    val id: String = "",
    val content: String = "",
    val role: String = "user",
    val timestamp: Long = System.currentTimeMillis()
)
