package com.myai.android.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.myai.android.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TopBar(
    agentName: String = "MyAI",
    isConnected: Boolean = false,
    onSettingsClick: () -> Unit = {}
) {
    TopAppBar(
        title = {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Box(modifier = Modifier.size(10.dp).clip(CircleShape).background(if (isConnected) SuccessGreen else ErrorRed))
                Column {
                    Text(agentName, fontSize = 18.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
                    Text(if (isConnected) "Connected" else "Disconnected", fontSize = 11.sp, color = if (isConnected) SuccessGreen else ErrorRed)
                }
            }
        },
        actions = {
            IconButton(onClick = onSettingsClick) {
                Icon(Icons.Default.Settings, "Settings", tint = TextSecondary)
            }
        },
        colors = TopAppBarDefaults.topAppBarColors(containerColor = DarkSurface)
    )
}
