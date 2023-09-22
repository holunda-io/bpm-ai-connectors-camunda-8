package io.holunda.connector.translate

import com.fasterxml.jackson.databind.node.*
import io.holunda.connector.*
import io.holunda.connector.generic.*
import io.holunda.connector.translate.*
import io.mockk.*
import org.junit.jupiter.api.*

class TranslateFunctionTest : AbstractFunctionTest<TranslateFunction>() {

    override val function = TranslateFunction()

    @Test
    fun `should execute extract function`() {
        val mockRequest = mockk<TranslateRequest>(relaxed = true)
        every { mockRequest.inputJson } returns TextNode("")
        val mockResult = TextNode("result")

        val result = executeFunctionTest(mockRequest, mockResult, TranslateRequest::class.java)

        verify { TranslateTask.fromRequest(mockRequest) }
        Assertions.assertInstanceOf(TranslateResult::class.java, result)
        Assertions.assertEquals(mockResult, (result as TranslateResult).result)
    }
}
