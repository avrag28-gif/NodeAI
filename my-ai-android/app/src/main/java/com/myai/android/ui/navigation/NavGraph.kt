package com.myai.android.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.myai.android.ui.chat.ChatScreen
import com.myai.android.ui.settings.PermissionSettingsScreen
import com.myai.android.ui.settings.ServerConfigScreen
import com.myai.android.ui.settings.SettingsScreen

object Routes {
    const val CHAT = "chat"
    const val SETTINGS = "settings"
    const val SERVER_CONFIG = "server_config"
    const val PERMISSIONS = "permissions"
}

@Composable
fun MyAINavigation() {
    val nav = rememberNavController()
    NavHost(navController = nav, startDestination = Routes.CHAT) {
        composable(Routes.CHAT) { ChatScreen(onSettingsClick = { nav.navigate(Routes.SETTINGS) }) }
        composable(Routes.SETTINGS) {
            SettingsScreen(
                onBackClick = { nav.popBackStack() },
                onServerConfigClick = { nav.navigate(Routes.SERVER_CONFIG) },
                onPermissionSettingsClick = { nav.navigate(Routes.PERMISSIONS) }
            )
        }
        composable(Routes.SERVER_CONFIG) { ServerConfigScreen(onBackClick = { nav.popBackStack() }) }
        composable(Routes.PERMISSIONS) { PermissionSettingsScreen(onBackClick = { nav.popBackStack() }) }
    }
}
