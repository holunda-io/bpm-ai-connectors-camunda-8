package io.holunda.connector

import org.springframework.boot.SpringApplication
import org.springframework.boot.autoconfigure.SpringBootApplication


fun main(args: Array<String>) {
  SpringApplication.run(LocalConnectorRuntime::class.java, *args)
}

@SpringBootApplication
open class LocalConnectorRuntime
