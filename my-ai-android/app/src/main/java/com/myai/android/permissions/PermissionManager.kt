package com.myai.android.permissions

import android.content.Context
import com.myai.android.domain.model.PermissionState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class PermissionManager(private val context: Context) {
    private val _permissions = MutableStateFlow<Map<String, PermissionState>>(emptyMap())
    val permissions: StateFlow<Map<String, PermissionState>> = _permissions

    fun getState(toolName: String): PermissionState {
        return _permissions.value[toolName] ?: PermissionState.ASK
    }

    fun setState(toolName: String, state: PermissionState) {
        _permissions.value = _permissions.value + (toolName to state)
    }

    fun isAllowed(toolName: String): Boolean = getState(toolName) == PermissionState.ALLOWED
    fun isDenied(toolName: String): Boolean = getState(toolName) == PermissionState.DENIED
}
