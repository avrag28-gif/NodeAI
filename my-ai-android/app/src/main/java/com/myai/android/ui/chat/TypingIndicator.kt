package com.myai.android.ui.chat

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.myai.android.ui.theme.*

@Composable
fun TypingIndicator(modifier: Modifier = Modifier) {
    val transition = rememberInfiniteTransition(label = "typing")
    val a1 by transition.animateFloat(0.3f, 1f, infiniteRepeatable(tween(600, easing = FastOutSlowInEasing), RepeatMode.Reverse), label = "d1")
    val a2 by transition.animateFloat(0.3f, 1f, infiniteRepeatable(tween(600, 200, easing = FastOutSlowInEasing), RepeatMode.Reverse), label = "d2")
    val a3 by transition.animateFloat(0.3f, 1f, infiniteRepeatable(tween(600, 400, easing = FastOutSlowInEasing), RepeatMode.Reverse), label = "d3")

    Row(modifier = modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(4.dp)) {
        Box(modifier = Modifier.size(8.dp).alpha(a1).clip(CircleShape).background(Cyan500))
        Box(modifier = Modifier.size(8.dp).alpha(a2).clip(CircleShape).background(Cyan500))
        Box(modifier = Modifier.size(8.dp).alpha(a3).clip(CircleShape).background(Cyan500))
        Spacer(modifier = Modifier.width(4.dp))
        Text("Thinking...", fontSize = 12.sp, color = TextMuted)
    }
}
