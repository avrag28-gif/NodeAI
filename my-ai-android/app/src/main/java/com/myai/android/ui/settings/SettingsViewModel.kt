package com.myai.android.ui.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.myai.android.data.model.ServerConfig
import com.myai.android.data.repository.SettingsRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val settingsRepository: SettingsRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(ServerConfig())
    val uiState: StateFlow<ServerConfig> = _uiState.asStateFlow()

    init { viewModelScope.launch { settingsRepository.serverConfig.collect { _uiState.value = it } } }

    fun updateHost(host: String) { _uiState.update { it.copy(host = host) } }
    fun updatePort(port: String) { port.toIntOrNull()?.let { p -> _uiState.update { it.copy(port = p) } } }
    fun updateToken(token: String) { _uiState.update { it.copy(authToken = token) } }
    fun save() { viewModelScope.launch { settingsRepository.saveServerConfig(_uiState.value) } }
}
