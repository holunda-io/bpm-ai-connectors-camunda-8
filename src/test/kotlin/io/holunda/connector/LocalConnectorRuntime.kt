package io.holunda.connector

import io.camunda.connector.runtime.ConnectorRuntimeApplication
import org.springframework.boot.SpringApplication

object LocalConnectorRuntime {
    @JvmStatic
    fun main(args: Array<String>) {
        SpringApplication.run(ConnectorRuntimeApplication::class.java, *args)
    }
}
