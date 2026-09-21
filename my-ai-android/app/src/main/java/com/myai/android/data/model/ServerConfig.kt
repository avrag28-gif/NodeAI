package com.myai.android.data.model

data class ServerConfig(
    val host: String = "192.168.1.100",
    val port: Int = 50080,
    val authToken: String = "",
    val useSsl: Boolean = false
) {
    val baseUrl: String get() = "http://$host:$port"
    val wsUrl: String get() = "ws://$host:$port"
}
