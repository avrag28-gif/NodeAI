package com.myai.android.permissions

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.myai.android.ui.theme.*

@Composable
fun PermissionDialog(
    toolName: String,
    onAllow: () -> Unit,
    onDeny: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDeny,
        containerColor = DarkSurface,
        titleContentColor = TextPrimary,
        textContentColor = TextSecondary,
        shape = RoundedCornerShape(16.dp),
        title = { Text("Permission Required", fontWeight = FontWeight.Bold) },
        text = { Text("Allow \"$toolName\" tool to access device features?", fontSize = 14.sp) },
        confirmButton = {
            Button(
                onClick = onAllow,
                colors = ButtonDefaults.buttonColors(containerColor = Cyan700, contentColor = TextPrimary)
            ) { Text("Allow") }
        },
        dismissButton = {
            TextButton(onClick = onDeny, colors = ButtonDefaults.textButtonColors(contentColor = ErrorRed)) {
                Text("Deny")
            }
        }
    )
}
