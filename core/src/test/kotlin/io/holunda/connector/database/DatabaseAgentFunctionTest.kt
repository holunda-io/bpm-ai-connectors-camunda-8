package io.holunda.connector.database

import com.fasterxml.jackson.databind.node.*
import io.holunda.connector.*
import io.holunda.connector.database.*
import io.mockk.*
import org.junit.jupiter.api.*

class DatabaseAgentFunctionTest : AbstractFunctionTest<DatabaseAgentFunction>() {

    override val function = DatabaseAgentFunction()

    @Test
    fun `should execute extract function`() {
        val mockRequest = mockk<DatabaseAgentRequest>(relaxed = true)
        every { mockRequest.inputJson } returns TextNode("")
        every { mockRequest.query.outputSchema } returns TextNode("")
        val mockResult = TextNode("result")

        val result = executeFunctionTest(mockRequest, mockResult, DatabaseAgentRequest::class.java)

        verify { DatabaseAgentTask.fromRequest(mockRequest) }
        Assertions.assertInstanceOf(DatabaseAgentResult::class.java, result)
        Assertions.assertEquals(mockResult, (result as DatabaseAgentResult).result)
    }
}
