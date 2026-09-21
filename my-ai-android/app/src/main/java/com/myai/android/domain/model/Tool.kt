package com.myai.android.domain.model

data class Tool(
    val name: String,
    val displayName: String,
    val description: String,
    val permissionRequired: String
)

object AvailableTools {
    val tools = listOf(
        Tool("flash", "Flashlight", "Toggle flashlight", "flash"),
        Tool("camera", "Camera", "Take photos", "camera"),
        Tool("files", "Files", "File operations", "files"),
        Tool("microphone", "Microphone", "Record audio", "microphone"),
        Tool("clipboard", "Clipboard", "Copy/paste", "clipboard"),
        Tool("notifications", "Notifications", "Show notifications", "notifications"),
        Tool("battery", "Battery", "Battery status", "battery"),
        Tool("apps", "Apps", "Launch apps", "apps"),
        Tool("wifi", "WiFi", "WiFi info", "wifi"),
        Tool("sms", "SMS", "Send SMS", "sms"),
        Tool("contacts", "Contacts", "Read contacts", "contacts")
    )
}
