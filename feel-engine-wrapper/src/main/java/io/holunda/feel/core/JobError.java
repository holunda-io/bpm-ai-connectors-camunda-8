package io.holunda.feel.core;

import java.time.Duration;
import java.util.Map;

public record JobError(
        String message, Map<String, Object> variables,
        Integer retries,
        Duration retryBackoff
) implements ConnectorError {}
