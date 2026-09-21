package com.myai.android.tools

import android.content.Context
import android.provider.ContactsContract

class ContactTool : ToolExecutor {
    override val toolName = "contacts"

    override suspend fun execute(action: String, params: Map<String, String>, context: Context): ToolResult {
        return try {
            val cursor = context.contentResolver.query(
                ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                arrayOf(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME, ContactsContract.CommonDataKinds.Phone.NUMBER),
                null, null, null
            )
            val contacts = mutableListOf<String>()
            cursor?.use {
                while (it.moveToNext()) {
                    val name = it.getString(0) ?: "Unknown"
                    val number = it.getString(1) ?: "N/A"
                    contacts.add("  $name: $number")
                }
            }
            ToolResult(true, "Contacts (${contacts.size}):\n${contacts.joinToString("\n")}")
        } catch (e: Exception) { ToolResult(false, error = e.message) }
    }
}
