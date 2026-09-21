package com.myai.android.di

import android.content.Context
import com.myai.android.data.api.ApiClient
import com.myai.android.data.api.WebSocketManager
import com.myai.android.data.repository.ChatRepository
import com.myai.android.data.repository.SettingsRepository
import com.myai.android.data.repository.ToolsRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides @Singleton fun provideApiClient() = ApiClient()
    @Provides @Singleton fun provideWsManager() = WebSocketManager()
    @Provides @Singleton fun provideChatRepo(api: ApiClient, ws: WebSocketManager) = ChatRepository(api, ws)
    @Provides @Singleton fun provideSettingsRepo(@ApplicationContext ctx: Context) = SettingsRepository(ctx)
    @Provides @Singleton fun provideToolsRepo(api: ApiClient) = ToolsRepository(api)
}
