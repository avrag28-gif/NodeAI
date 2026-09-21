package com.myai.android.tools

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import androidx.core.app.NotificationCompat

class NotificationTool : ToolExecutor {
    override val toolName = "notifications"
    private var notifId = 1000

    override suspend fun execute(action: String, params: Map<String, String>, context: Context): ToolResult {
        return try {
            val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            val channel = NotificationChannel("myai", "MyAI", NotificationManager.IMPORTANCE_DEFAULT)
            nm.createNotificationChannel(channel)

            when (action) {
                "show" -> {
                    val title = params["title"] ?: "MyAI"
                    val msg = params["message"] ?: return ToolResult(false, error = "Missing message")
                    val n = NotificationCompat.Builder(context, "myai")
                        .setSmallIcon(android.R.drawable.ic_dialog_info)
                        .setContentTitle(title).setContentText(msg).setAutoCancel(true).build()
                    nm.notify(notifId++, n)
                    ToolResult(true, "Notification shown")
                }
                "cancel_all" -> { nm.cancelAll(); ToolResult(true, "All cancelled") }
                else -> ToolResult(false, error = "Use show/cancel_all")
            }
        } catch (e: Exception) { ToolResult(false, error = e.message) }
    }
}
