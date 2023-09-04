package io.holunda.connector

import com.fasterxml.jackson.module.kotlin.*
import org.slf4j.*
import org.springframework.boot.SpringApplication
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration


fun main(args: Array<String>) {
  SpringApplication.run(LocalConnectorRuntime::class.java, *args)
}

@SpringBootApplication
class LocalConnectorRuntime

@Configuration
class JacksonConfig {

    @Bean
    fun objectMapper() = jacksonObjectMapper()
}
