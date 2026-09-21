package com.myai.android.data.api

import com.myai.android.data.model.ServerConfig
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.launch
import okhttp3.*
import org.json.JSONObject
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class WebSocketManager @Inject constructor() {
    private var webSocket: WebSocket? = null
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    private val _messages = MutableSharedFlow<String>(extraBufferCapacity = 64)
    val messages: SharedFlow<String> = _messages

    private val _connectionState = MutableSharedFlow<Boolean>(extraBufferCapacity = 8)
    val connectionState: SharedFlow<Boolean> = _connectionState

    fun connect(config: ServerConfig) {
        disconnect()
        val client = OkHttpClient.Builder().pingInterval(30, TimeUnit.SECONDS).build()
        val request = Request.Builder().url("${config.wsUrl}/ws").build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(ws: WebSocket, response: Response) {
                scope.launch { _connectionState.emit(true) }
            }
            override fun onMessage(ws: WebSocket, text: String) {
                scope.launch { _messages.emit(text) }
            }
            override fun onClosing(ws: WebSocket, code: Int, reason: String) {
                ws.close(1000, null)
                scope.launch { _connectionState.emit(false) }
            }
            override fun onFailure(ws: WebSocket, t: Throwable, response: Response?) {
                scope.launch { _connectionState.emit(false) }
            }
        })
    }

    fun sendMessage(message: String) {
        webSocket?.send(message)
    }

    fun disconnect() {
        webSocket?.close(1000, null)
        webSocket = null
    }

    fun isConnected(): Boolean = webSocket != null
}
