package com.myai.android.tools

import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager

class AppLauncherTool : ToolExecutor {
    override val toolName = "apps"

    override suspend fun execute(action: String, params: Map<String, String>, context: Context): ToolResult {
        return try {
            val pm = context.packageManager
            when (action) {
                "list" -> {
                    val apps = pm.getInstalledApplications(0)
                        .filter { pm.getLaunchIntentForPackage(it.packageName) != null }
                        .map { "  ${it.loadLabel(pm)} (${it.packageName})" }
                        .sorted()
                    ToolResult(true, "Apps:\n${apps.joinToString("\n")}")
                }
                "launch" -> {
                    val pkg = params["package"] ?: return ToolResult(false, error = "Missing package")
                    val intent = pm.getLaunchIntentForPackage(pkg)
                    if (intent != null) {
                        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                        context.startActivity(intent)
                        ToolResult(true, "Launched: $pkg")
                    } else ToolResult(false, error = "App not found: $pkg")
                }
                else -> ToolResult(false, error = "Use list/launch")
            }
        } catch (e: Exception) { ToolResult(false, error = e.message) }
    }
}
