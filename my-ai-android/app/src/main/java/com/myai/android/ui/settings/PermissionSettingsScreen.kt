package com.myai.android.ui.settings

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.myai.android.domain.model.AvailableTools
import com.myai.android.domain.model.PermissionState
import com.myai.android.permissions.PermissionPolicy
import com.myai.android.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PermissionSettingsScreen(onBackClick: () -> Unit = {}) {
    val policy = remember { PermissionPolicy() }
    var policies by remember { mutableStateOf(policy.getAll()) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Permissions", fontWeight = FontWeight.Bold, color = TextPrimary) },
                navigationIcon = { IconButton(onClick = onBackClick) { Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back", tint = TextPrimary) } },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = DarkSurface)
            )
        },
        containerColor = DarkBackground
    ) { padding ->
        LazyColumn(modifier = Modifier.fillMaxSize().padding(padding), contentPadding = PaddingValues(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            item { Text("Tool Permissions", fontSize = 12.sp, fontWeight = FontWeight.Medium, color = Cyan500, modifier = Modifier.padding(start = 4.dp)) }
            items(AvailableTools.tools.size) { index ->
                val tool = AvailableTools.tools[index]
                val current = policies[tool.name] ?: PermissionState.ASK
                Surface(modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp)), color = DarkSurface) {
                    Row(modifier = Modifier.fillMaxWidth().padding(16.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(tool.displayName, fontSize = 16.sp, color = TextPrimary)
                            Text(tool.description, fontSize = 12.sp, color = TextSecondary)
                        }
                        Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                            FilterChip(selected = current == PermissionState.ALLOWED, onClick = { policy.setState(tool.name, PermissionState.ALLOWED); policies = policy.getAll() },
                                label = { Text("Allow", fontSize = 11.sp) },
                                colors = FilterChipDefaults.filterChipColors(selectedContainerColor = SuccessGreen.copy(alpha = 0.2f), selectedLabelColor = SuccessGreen))
                            FilterChip(selected = current == PermissionState.ASK, onClick = { policy.setState(tool.name, PermissionState.ASK); policies = policy.getAll() },
                                label = { Text("Ask", fontSize = 11.sp) },
                                colors = FilterChipDefaults.filterChipColors(selectedContainerColor = WarningOrange.copy(alpha = 0.2f), selectedLabelColor = WarningOrange))
                            FilterChip(selected = current == PermissionState.DENIED, onClick = { policy.setState(tool.name, PermissionState.DENIED); policies = policy.getAll() },
                                label = { Text("Deny", fontSize = 11.sp) },
                                colors = FilterChipDefaults.filterChipColors(selectedContainerColor = ErrorRed.copy(alpha = 0.2f), selectedLabelColor = ErrorRed))
                        }
                    }
                }
            }
        }
    }
}
