package com.myai.android.data.model

data class AgentStatus(
    val connected: Boolean = false,
    val agentName: String = "MyAI",
    val model: String = "",
    val status: String = "disconnected"
)
