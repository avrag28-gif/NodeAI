package com.myai.android.tools

import android.content.Context
import java.io.File

class FileTool : ToolExecutor {
    override val toolName = "files"

    override suspend fun execute(action: String, params: Map<String, String>, context: Context): ToolResult {
        return try {
            when (action) {
                "read" -> {
                    val path = params["path"] ?: return ToolResult(false, error = "Missing path")
                    val file = File(path)
                    if (file.exists()) ToolResult(true, file.readText()) else ToolResult(false, error = "File not found")
                }
                "write" -> {
                    val path = params["path"] ?: return ToolResult(false, error = "Missing path")
                    val content = params["content"] ?: return ToolResult(false, error = "Missing content")
                    File(path).parentFile?.mkdirs()
                    File(path).writeText(content)
                    ToolResult(true, "Written: $path")
                }
                "list" -> {
                    val path = params["path"] ?: context.filesDir.absolutePath
                    val files = File(path).listFiles() ?: emptyArray()
                    ToolResult(true, files.joinToString("\n") { if (it.isDirectory) "[DIR] ${it.name}" else "[FILE] ${it.name}" })
                }
                "delete" -> {
                    val path = params["path"] ?: return ToolResult(false, error = "Missing path")
                    val file = File(path)
                    if (file.exists()) { file.delete(); ToolResult(true, "Deleted: $path") } else ToolResult(false, error = "Not found")
                }
                else -> ToolResult(false, error = "Use read/write/list/delete")
            }
        } catch (e: Exception) { ToolResult(false, error = e.message) }
    }
}
