package io.holunda.feel.core;

import com.fasterxml.jackson.annotation.JsonSubTypes;
import com.fasterxml.jackson.annotation.JsonSubTypes.Type;
import com.fasterxml.jackson.annotation.JsonTypeInfo;
import com.fasterxml.jackson.annotation.JsonTypeInfo.Id;

import static io.camunda.connector.feel.FeelConnectorFunctionProvider.*;

@JsonTypeInfo(use = Id.NAME, property = ERROR_TYPE_PROPERTY)
@JsonSubTypes({
        @Type(value = BpmnError.class, name = BPMN_ERROR_TYPE_VALUE),
        @Type(value = JobError.class, name = JOB_ERROR_TYPE_VALUE)
})
public sealed interface ConnectorError permits BpmnError, JobError {
}