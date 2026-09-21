package com.myai.android.data.api

import android.content.Context
import com.myai.android.data.model.ServerConfig
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ApiClient @Inject constructor() {
    private var api: AgentApi? = null
    private var currentConfig: ServerConfig? = null

    fun configure(config: ServerConfig) {
        if (currentConfig == config && api != null) return
        currentConfig = config

        val builder = OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)

        if (config.authToken.isNotEmpty()) {
            builder.addInterceptor { chain ->
                val request = chain.request().newBuilder()
                    .addHeader("Authorization", "Bearer ${config.authToken}")
                    .build()
                chain.proceed(request)
            }
        }

        api = Retrofit.Builder()
            .baseUrl(config.baseUrl + "/")
            .client(builder.build())
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(AgentApi::class.java)
    }

    fun getApi(): AgentApi {
        if (api == null) configure(ServerConfig())
        return api!!
    }
}
