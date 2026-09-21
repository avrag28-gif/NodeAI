package com.myai.android.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.myai.android.ui.theme.*

@Composable
fun StatusIndicator(isConnected: Boolean) {
    Row(modifier = Modifier.padding(8.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        Box(modifier = Modifier.size(8.dp).clip(CircleShape).background(if (isConnected) SuccessGreen else ErrorRed))
        Text(if (isConnected) "Online" else "Offline", fontSize = 12.sp, color = if (isConnected) SuccessGreen else ErrorRed)
    }
}
