package io.holunda.connector;

import org.junit.jupiter.api.Test;

public class TestCreateProcess {

  @Test
  public void testCreateProcess() {
    var creator = new ProcessModelCreator();//new ProcessModelCreatorBreadthFirst();

    var nodes = creator.parseJsonFile("/elements.json");
    var edges = creator.parseJsonFileString("/flows.json");

    var model = creator.createProcess(nodes, edges);

    creator.writeModelToFile(model, "process.bpmn");
  }

}
