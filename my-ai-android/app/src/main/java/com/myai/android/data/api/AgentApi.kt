package com.myai.android.data.api

import com.myai.android.data.model.*
import retrofit2.http.*

interface AgentApi {
    @POST("api/chat")
    suspend fun sendMessage(@Body request: Map<String, String>): Map<String, Any>

    @GET("api/status")
    suspend fun getStatus(): Map<String, Any>

    @POST("api/tool/execute")
    suspend fun executeTool(@Body request: ToolRequest): ToolResponse
}
