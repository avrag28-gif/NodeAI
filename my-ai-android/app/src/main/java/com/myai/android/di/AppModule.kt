package com.myai.android.di

import android.content.Context
import com.myai.android.data.api.ApiClient
import com.myai.android.data.api.WebSocketManager
import com.myai.android.data.repository.ChatRepository
import com.myai.android.data.repository.SettingsRepository
import com.myai.android.data.repository.ToolsRepository
import com.myai.android.tools.*
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides @Singleton fun provideFlashlight() = FlashlightTool()
    @Provides @Singleton fun provideCamera() = CameraTool()
    @Provides @Singleton fun provideFiles() = FileTool()
    @Provides @Singleton fun provideMic() = MicrophoneTool()
    @Provides @Singleton fun provideClipboard() = ClipboardTool()
    @Provides @Singleton fun provideNotif() = NotificationTool()
    @Provides @Singleton fun provideBattery() = BatteryTool()
    @Provides @Singleton fun provideApps() = AppLauncherTool()
    @Provides @Singleton fun provideWifi() = WifiTool()
    @Provides @Singleton fun provideSms() = SmsTool()
    @Provides @Singleton fun provideContacts() = ContactTool()
    @Provides @Singleton fun provideToolExecutors(
        f: FlashlightTool, c: CameraTool, fi: FileTool, m: MicrophoneTool,
        cl: ClipboardTool, n: NotificationTool, b: BatteryTool, a: AppLauncherTool,
        w: WifiTool, s: SmsTool, co: ContactTool
    ): List<ToolExecutor> = listOf(f, c, fi, m, cl, n, b, a, w, s, co)
}
