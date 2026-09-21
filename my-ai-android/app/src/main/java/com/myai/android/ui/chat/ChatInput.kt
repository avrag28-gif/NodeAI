package com.myai.android.ui.chat

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.myai.android.ui.theme.*

@Composable
fun ChatInput(onSendMessage: (String) -> Unit, modifier: Modifier = Modifier, isLoading: Boolean = false) {
    var text by remember { mutableStateOf("") }
    val keyboardController = LocalSoftwareKeyboardController.current

    Surface(modifier = modifier, color = DarkSurface, shadowElevation = 8.dp) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            OutlinedTextField(
                value = text, onValueChange = { text = it },
                modifier = Modifier.weight(1f),
                placeholder = { Text("Message MyAI...", color = TextMuted, fontSize = 14.sp) },
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = Cyan500, unfocusedBorderColor = DarkSurfaceVariant,
                    cursorColor = Cyan500, focusedTextColor = TextPrimary, unfocusedTextColor = TextPrimary
                ),
                shape = RoundedCornerShape(24.dp),
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                keyboardActions = KeyboardActions(onSend = {
                    if (text.isNotBlank() && !isLoading) { onSendMessage(text.trim()); text = ""; keyboardController?.hide() }
                }),
                maxLines = 4, enabled = !isLoading
            )
            IconButton(
                onClick = { if (text.isNotBlank() && !isLoading) { onSendMessage(text.trim()); text = ""; keyboardController?.hide() } },
                enabled = text.isNotBlank() && !isLoading,
                modifier = Modifier.size(48.dp).clip(RoundedCornerShape(24.dp))
                    .background(if (text.isNotBlank() && !isLoading) Cyan500 else DarkSurfaceVariant)
            ) {
                Icon(Icons.AutoMirrored.Filled.Send, "Send", tint = if (text.isNotBlank() && !isLoading) DarkBackground else TextMuted, modifier = Modifier.size(20.dp))
            }
        }
    }
}
