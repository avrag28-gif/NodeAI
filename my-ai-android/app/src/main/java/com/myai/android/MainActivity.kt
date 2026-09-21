package com.myai.android

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.myai.android.ui.navigation.MyAINavigation
import com.myai.android.ui.theme.DarkBackground
import com.myai.android.ui.theme.MyAITheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MyAITheme {
                Surface(modifier = Modifier.fillMaxSize(), color = DarkBackground) {
                    MyAINavigation()
                }
            }
        }
    }
}
