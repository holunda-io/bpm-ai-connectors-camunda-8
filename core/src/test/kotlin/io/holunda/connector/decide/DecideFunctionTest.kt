package io.holunda.connector.decide

import com.fasterxml.jackson.databind.node.*
import io.holunda.connector.*
import io.mockk.*
import org.junit.jupiter.api.*

class DecideFunctionTest : AbstractFunctionTest<DecideFunction>() {

    override val function = DecideFunction()

    @Test
    fun `should execute extract function`() {
        val mockRequest = mockk<DecideRequest>(relaxed = true)
        every { mockRequest.inputJson } returns TextNode("")
        val mockResult = TextNode("result")

        val result = executeFunctionTest(mockRequest, mockResult, DecideRequest::class.java)

        verify { DecideTask.fromRequest(mockRequest) }
        Assertions.assertInstanceOf(DecideResult::class.java, result)
        Assertions.assertEquals(mockResult, (result as DecideResult).result)
    }
}
