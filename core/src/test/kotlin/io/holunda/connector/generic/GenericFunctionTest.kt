package io.holunda.connector.generic

import com.fasterxml.jackson.databind.node.*
import io.holunda.connector.*
import io.holunda.connector.generic.*
import io.mockk.*
import org.junit.jupiter.api.*

class GenericFunctionTest : AbstractFunctionTest<GenericFunction>() {

    override val function = GenericFunction()

    @Test
    fun `should execute extract function`() {
        val mockRequest = mockk<GenericRequest>(relaxed = true)
        every { mockRequest.inputJson } returns TextNode("")
        val mockResult = TextNode("result")

        val result = executeFunctionTest(mockRequest, mockResult, GenericRequest::class.java)

        verify { GenericTask.fromRequest(mockRequest) }
        Assertions.assertInstanceOf(GenericResult::class.java, result)
        Assertions.assertEquals(mockResult, (result as GenericResult).result)
    }
}
