package io.holunda.connector;

import io.camunda.connector.runtime.ConnectorRuntimeApplication;
import org.springframework.boot.SpringApplication;

public class LocalConnectorRuntime {

  public static void main(String[] args) {
    SpringApplication.run(ConnectorRuntimeApplication.class, args);
  }
}
