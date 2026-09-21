package com.myai.android.data.repository

import com.myai.android.data.api.ApiClient
import com.myai.android.data.model.ToolRequest
import com.myai.android.data.model.ToolResponse
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ToolsRepository @Inject constructor(
    private val apiClient: ApiClient
) {
    suspend fun executeTool(tool: String, action: String, params: Map<String, String> = emptyMap()): Result<ToolResponse> {
        return try {
            val response = apiClient.getApi().executeTool(ToolRequest(tool, action, params))
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
