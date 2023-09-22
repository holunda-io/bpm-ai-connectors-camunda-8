package io.holunda.connector

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.TextNode
import io.camunda.connector.api.outbound.*
import io.holunda.connector.common.*
import io.mockk.*
import okhttp3.mockwebserver.*
import org.junit.jupiter.api.*
import org.junit.jupiter.api.Assertions.*

abstract class AbstractFunctionTest<F: OutboundConnectorFunction> {

    protected lateinit var mockWebServer: MockWebServer
    protected abstract val function: F

    @BeforeEach
    fun setup() {
        mockWebServer = MockWebServer().also { it.start() }
        LLMServiceClient.llmServiceUrl = mockWebServer.url("/").toString()
    }

    @AfterEach
    fun teardown() = mockWebServer.shutdown()

    protected fun executeFunctionTest(mockRequest: Any, mockResult: JsonNode, requestClass: Class<*>): Any {
        // Arrange
        val mockContext = mockk<OutboundConnectorContext>()
        every { mockContext.bindVariables(requestClass) } returns mockRequest
        mockWebServer.enqueue(MockResponse().setBody(mockResult.toString()))

        // Act
        val result = function.execute(mockContext)

        // Assert
        verify { mockContext.bindVariables(requestClass) }

        return result
    }
}
