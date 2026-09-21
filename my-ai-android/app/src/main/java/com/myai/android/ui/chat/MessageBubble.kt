package com.myai.android.ui.chat

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.SmartToy
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.myai.android.domain.model.Message
import com.myai.android.ui.theme.*
import java.text.SimpleDateFormat
import java.util.*

@Composable
fun MessageBubble(message: Message, modifier: Modifier = Modifier) {
    Row(
        modifier = modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 4.dp),
        horizontalArrangement = if (message.isUser) Arrangement.End else Arrangement.Start,
        verticalAlignment = Alignment.Top
    ) {
        if (!message.isUser) {
            Box(modifier = Modifier.size(32.dp).clip(RoundedCornerShape(8.dp)).background(Cyan700), contentAlignment = Alignment.Center) {
                Icon(Icons.Default.SmartToy, "AI", tint = TextPrimary, modifier = Modifier.size(18.dp))
            }
            Spacer(modifier = Modifier.width(8.dp))
        }

        Column(modifier = Modifier.widthIn(max = 300.dp), horizontalAlignment = if (message.isUser) Alignment.End else Alignment.Start) {
            Surface(
                shape = RoundedCornerShape(
                    topStart = if (message.isUser) 16.dp else 4.dp,
                    topEnd = if (message.isUser) 4.dp else 16.dp,
                    bottomStart = 16.dp, bottomEnd = 16.dp
                ),
                color = if (message.isUser) UserMessageBg else AgentMessageBg
            ) {
                Text(
                    text = message.content,
                    modifier = Modifier.padding(12.dp),
                    fontSize = 14.sp,
                    lineHeight = 20.sp,
                    color = if (message.isError) ErrorRed else TextPrimary
                )
            }
            Text(
                text = SimpleDateFormat("HH:mm", Locale.getDefault()).format(Date(message.timestamp)),
                fontSize = 10.sp, color = TextMuted,
                modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
            )
        }

        if (message.isUser) {
            Spacer(modifier = Modifier.width(8.dp))
            Box(modifier = Modifier.size(32.dp).clip(RoundedCornerShape(8.dp)).background(Blue700), contentAlignment = Alignment.Center) {
                Icon(Icons.Default.Person, "User", tint = TextPrimary, modifier = Modifier.size(18.dp))
            }
        }
    }
}
