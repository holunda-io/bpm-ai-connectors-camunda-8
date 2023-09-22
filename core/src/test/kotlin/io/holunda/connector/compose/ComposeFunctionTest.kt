package io.holunda.connector.compose

import com.fasterxml.jackson.databind.node.*
import io.holunda.connector.*
import io.mockk.*
import org.junit.jupiter.api.*

class ComposeFunctionTest : AbstractFunctionTest<ComposeFunction>() {

    override val function = ComposeFunction()

    @Test
    fun `should execute compose function`() {
        val mockRequest = mockk<ComposeRequest>(relaxed = true)
        every { mockRequest.inputJson } returns TextNode("")
        val mockResult = TextNode("result")

        val result = executeFunctionTest(mockRequest, mockResult, ComposeRequest::class.java)

        verify { ComposeTask.fromRequest(mockRequest) }
        Assertions.assertInstanceOf(ComposeResult::class.java, result)
        Assertions.assertEquals(mockResult, (result as ComposeResult).result)
    }
}
