package com.myai.android.ui.chat

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.myai.android.ui.components.TopBar
import com.myai.android.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(onSettingsClick: () -> Unit = {}, viewModel: ChatViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsState()
    val listState = rememberLazyListState()

    LaunchedEffect(uiState.messages.size) {
        if (uiState.messages.isNotEmpty()) listState.animateScrollToItem(uiState.messages.size - 1)
    }

    Scaffold(
        topBar = { TopBar(isConnected = uiState.isConnected, onSettingsClick = onSettingsClick) },
        bottomBar = { ChatInput(onSendMessage = { viewModel.sendMessage(it) }, isLoading = uiState.isLoading) },
        containerColor = DarkBackground
    ) { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding).background(DarkBackground)) {
            if (uiState.messages.isEmpty()) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("MyAI", style = MaterialTheme.typography.headlineLarge, color = Cyan500)
                        Text("Your personal AI assistant", style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
                        Text("Type a message to start", style = MaterialTheme.typography.bodySmall, color = TextMuted)
                    }
                }
            } else {
                LazyColumn(state = listState, modifier = Modifier.fillMaxSize(), contentPadding = PaddingValues(vertical = 8.dp)) {
                    items(uiState.messages) { msg -> MessageBubble(message = msg) }
                    if (uiState.isLoading) item { TypingIndicator() }
                }
            }
        }
    }
}
