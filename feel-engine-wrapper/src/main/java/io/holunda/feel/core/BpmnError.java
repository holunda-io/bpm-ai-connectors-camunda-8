package io.holunda.feel.core;

import java.util.Collections;
import java.util.Map;

/**
 * Container record for BPMN error data. This is used to indicate when a BPMN error should be
 * thrown.
 */
public record BpmnError(
        String code,
        String message,
        Map<String, Object> variables
) implements ConnectorError {
    public BpmnError {
        if (variables == null) {
            variables = Collections.emptyMap();
        }
    }

    public boolean hasCode() {
        return code != null;
    }
}