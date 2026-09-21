package com.myai.android.ui.chat

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.myai.android.data.api.WebSocketManager
import com.myai.android.data.repository.ChatRepository
import com.myai.android.data.repository.SettingsRepository
import com.myai.android.domain.model.Message
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.util.UUID
import javax.inject.Inject

data class ChatUiState(
    val messages: List<Message> = emptyList(),
    val isLoading: Boolean = false,
    val isConnected: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class ChatViewModel @Inject constructor(
    private val chatRepository: ChatRepository,
    private val settingsRepository: SettingsRepository,
    private val webSocketManager: WebSocketManager
) : ViewModel() {
    private val _uiState = MutableStateFlow(ChatUiState())
    val uiState: StateFlow<ChatUiState> = _uiState.asStateFlow()

    init {
        connect()
        observeWs()
    }

    private fun connect() {
        viewModelScope.launch {
            settingsRepository.serverConfig.collect { config ->
                chatRepository.connectWebSocket(config)
            }
        }
    }

    private fun observeWs() {
        viewModelScope.launch { webSocketManager.connectionState.collect { _uiState.update { s -> s.copy(isConnected = it) } } }
        viewModelScope.launch {
            webSocketManager.messages.collect { msg ->
                if (msg == "__DONE__") _uiState.update { it.copy(isLoading = false) }
                else {
                    val agentMsg = Message(id = UUID.randomUUID().toString(), content = msg, isUser = false)
                    _uiState.update { it.copy(messages = it.messages + agentMsg, isLoading = false) }
                }
            }
        }
    }

    fun sendMessage(content: String) {
        val userMsg = Message(id = UUID.randomUUID().toString(), content = content, isUser = true)
        _uiState.update { it.copy(messages = it.messages + userMsg, isLoading = true) }
        viewModelScope.launch {
            if (webSocketManager.isConnected()) chatRepository.sendViaWebSocket(content)
            else {
                chatRepository.sendMessage(content).fold(
                    onSuccess = { resp ->
                        val agentMsg = Message(id = UUID.randomUUID().toString(), content = resp, isUser = false)
                        _uiState.update { it.copy(messages = it.messages + agentMsg, isLoading = false) }
                    },
                    onFailure = { e ->
                        val errMsg = Message(id = UUID.randomUUID().toString(), content = "Error: ${e.message}", isUser = false, isError = true)
                        _uiState.update { it.copy(messages = it.messages + errMsg, isLoading = false) }
                    }
                )
            }
        }
    }
}
