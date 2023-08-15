package io.holunda.connector

import org.slf4j.*
import org.springframework.boot.SpringApplication
import org.springframework.boot.autoconfigure.SpringBootApplication


fun main(args: Array<String>) {
  LoggerFactory.getLogger("").info("!!!!!!!!!!!" + System.getenv("ZEEBE_CLIENT_CLOUD_CLUSTER-ID"))
  SpringApplication.run(LocalConnectorRuntime::class.java, *args)
}

@SpringBootApplication
open class LocalConnectorRuntime
