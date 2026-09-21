package com.myai.android.permissions

import com.myai.android.domain.model.PermissionState

class PermissionPolicy {
    private val policies = mutableMapOf(
        "flash" to PermissionState.ALLOWED,
        "camera" to PermissionState.ASK,
        "microphone" to PermissionState.ASK,
        "files" to PermissionState.ASK,
        "sms" to PermissionState.DENIED,
        "contacts" to PermissionState.DENIED,
        "notifications" to PermissionState.ALLOWED,
        "clipboard" to PermissionState.ALLOWED,
        "wifi" to PermissionState.ALLOWED,
        "battery" to PermissionState.ALLOWED,
        "apps" to PermissionState.ASK
    )

    fun getState(tool: String) = policies[tool] ?: PermissionState.ASK
    fun setState(tool: String, state: PermissionState) { policies[tool] = state }
    fun getAll() = policies.toMap()
}
