package com.myai.android.data.repository

import com.myai.android.data.api.ApiClient
import com.myai.android.data.api.WebSocketManager
import com.myai.android.data.model.*
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ChatRepository @Inject constructor(
    private val apiClient: ApiClient,
    private val webSocketManager: WebSocketManager
) {
    private val chatHistory = mutableListOf<ChatMessage>()

    fun connectWebSocket(config: ServerConfig) = webSocketManager.connect(config)
    fun disconnectWebSocket() = webSocketManager.disconnect()
    fun sendViaWebSocket(message: String) = webSocketManager.sendMessage(message)
    fun getMessages() = webSocketManager.messages
    fun getConnectionState() = webSocketManager.connectionState

    suspend fun sendMessage(message: String): Result<String> {
        return try {
            val response = apiClient.getApi().sendMessage(mapOf("message" to message))
            Result.success(response["response"]?.toString() ?: "No response")
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun getChatHistory(): List<ChatMessage> = chatHistory.toList()
    fun addMessage(message: ChatMessage) { chatHistory.add(message) }
    fun clearHistory() { chatHistory.clear() }
}
