package com.myai.android.ui.settings

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.myai.android.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ServerConfigScreen(onBackClick: () -> Unit = {}, viewModel: SettingsViewModel = hiltViewModel()) {
    val config by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Server Configuration", fontWeight = FontWeight.Bold, color = TextPrimary) },
                navigationIcon = { IconButton(onClick = onBackClick) { Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back", tint = TextPrimary) } },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = DarkSurface)
            )
        },
        containerColor = DarkBackground
    ) { padding ->
        Column(
            modifier = Modifier.fillMaxSize().padding(padding).verticalScroll(rememberScrollState()).padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text("Agent Server", fontSize = 12.sp, fontWeight = FontWeight.Medium, color = Cyan500)
            Surface(modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp)), color = DarkSurface) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                    OutlinedTextField(
                        value = config.host, onValueChange = { viewModel.updateHost(it) },
                        label = { Text("Host IP", color = TextSecondary) },
                        placeholder = { Text("192.168.1.100", color = TextMuted) },
                        modifier = Modifier.fillMaxWidth(), singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Cyan500, unfocusedBorderColor = DarkSurfaceVariant,
                            cursorColor = Cyan500, focusedTextColor = TextPrimary, unfocusedTextColor = TextPrimary
                        )
                    )
                    OutlinedTextField(
                        value = config.port.toString(), onValueChange = { viewModel.updatePort(it) },
                        label = { Text("Port", color = TextSecondary) },
                        placeholder = { Text("50080", color = TextMuted) },
                        modifier = Modifier.fillMaxWidth(), singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Cyan500, unfocusedBorderColor = DarkSurfaceVariant,
                            cursorColor = Cyan500, focusedTextColor = TextPrimary, unfocusedTextColor = TextPrimary
                        )
                    )
                    OutlinedTextField(
                        value = config.authToken, onValueChange = { viewModel.updateToken(it) },
                        label = { Text("Auth Token", color = TextSecondary) },
                        placeholder = { Text("Optional", color = TextMuted) },
                        modifier = Modifier.fillMaxWidth(), singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Cyan500, unfocusedBorderColor = DarkSurfaceVariant,
                            cursorColor = Cyan500, focusedTextColor = TextPrimary, unfocusedTextColor = TextPrimary
                        )
                    )
                }
            }
            Button(
                onClick = { viewModel.save() },
                modifier = Modifier.fillMaxWidth().height(48.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Cyan500, contentColor = DarkBackground),
                shape = RoundedCornerShape(12.dp)
            ) { Text("Save Configuration", fontWeight = FontWeight.Bold) }
        }
    }
}
