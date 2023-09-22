package io.holunda.connector.retrieval

import com.fasterxml.jackson.databind.node.*
import io.holunda.connector.*
import io.holunda.connector.generic.*
import io.holunda.connector.retrieval.*
import io.mockk.*
import org.junit.jupiter.api.*

class RetrievalFunctionTest : AbstractFunctionTest<RetrievalFunction>() {

    override val function = RetrievalFunction()

    @Test
    fun `should execute extract function`() {
        val mockRequest = mockk<RetrievalRequest>(relaxed = true)
        every { mockRequest.advanced.fieldMetadata } returns TextNode("")
        every { mockRequest.query.outputSchema } returns TextNode("")
        val mockResult = TextNode("result")

        val result = executeFunctionTest(mockRequest, mockResult, RetrievalRequest::class.java)

        verify { RetrievalTask.fromRequest(mockRequest) }
        Assertions.assertInstanceOf(RetrievalResult::class.java, result)
        Assertions.assertEquals(mockResult, (result as RetrievalResult).result)
    }
}
