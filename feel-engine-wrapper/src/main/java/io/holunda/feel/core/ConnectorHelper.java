package io.holunda.feel.core;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import io.camunda.connector.feel.FeelEngineWrapper;
import io.camunda.connector.feel.FeelEngineWrapperException;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/**
 * The ConnectorHelper provide utility functions used to build connector runtimes.
 */
public class ConnectorHelper {

    public static FeelEngineWrapper FEEL_ENGINE_WRAPPER = new FeelEngineWrapper();

    public static ObjectMapper OBJECT_MAPPER = new ObjectMapper().registerModule(new JavaTimeModule());

    private static final String ERROR_CANNOT_PARSE_VARIABLES = "Cannot parse '%s' as '%s'.";

    public static Map<String, Object> createOutputVariables(
            final Object responseContent,
            final String resultExpression
    ) {
        final Map<String, Object> outputVariables = new HashMap<>();

        Optional.ofNullable(resultExpression)
                .filter(s -> !s.isBlank())
                .map(expression -> FEEL_ENGINE_WRAPPER.evaluateToJson(expression, responseContent))
                .map(json -> parseJsonVarsAsTypeOrThrow(json, Map.class, resultExpression))
                .ifPresent(outputVariables::putAll);

        return outputVariables;
    }

    public static Optional<ConnectorError> examineErrorExpression(
            final Object responseContent,
            final String errorExpression
    ) {
        return Optional.ofNullable(errorExpression)
                .filter(s -> !s.isBlank())
                .map(expression -> FEEL_ENGINE_WRAPPER.evaluateToJson(expression, responseContent))
                .filter(json -> !json.equals("null"))
                .filter(json -> !parseJsonVarsAsTypeOrThrow(json, Map.class, errorExpression).isEmpty())
                .map(json -> parseJsonVarsAsTypeOrThrow(json, ConnectorError.class, errorExpression))
                .filter(error -> {
                            if (error instanceof BpmnError bpmnError) {
                                return bpmnError.hasCode();
                            }
                            return true;
                        });
    }

    private static <T> T parseJsonVarsAsTypeOrThrow(
            final String jsonVars, Class<T> type,
            final String expression
    ) {
        try {
            return OBJECT_MAPPER.readValue(jsonVars, type);
        } catch (JsonProcessingException e) {
            throw new FeelEngineWrapperException(
                    String.format(ERROR_CANNOT_PARSE_VARIABLES, jsonVars, type.getName()),
                    expression,
                    jsonVars,
                    e
            );
        }
    }
}
