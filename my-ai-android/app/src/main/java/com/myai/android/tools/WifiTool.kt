package com.myai.android.tools

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities

class WifiTool : ToolExecutor {
    override val toolName = "wifi"

    override suspend fun execute(action: String, params: Map<String, String>, context: Context): ToolResult {
        return try {
            val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            val network = cm.activeNetwork
            val caps = network?.let { cm.getNetworkCapabilities(it) }
            val connected = caps != null
            val type = when {
                caps?.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) == true -> "WiFi"
                caps?.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) == true -> "Cellular"
                else -> "None"
            }
            ToolResult(true, "Connected: $connected | Type: $type")
        } catch (e: Exception) { ToolResult(false, error = e.message) }
    }
}
