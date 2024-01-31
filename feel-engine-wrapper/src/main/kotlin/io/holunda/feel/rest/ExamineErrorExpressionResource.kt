package io.holunda.feel.rest

import io.holunda.feel.core.*
import jakarta.ws.rs.*
import jakarta.ws.rs.core.MediaType
import jakarta.ws.rs.core.MediaType.*

@Path("/examineErrorExpression")
@Consumes(APPLICATION_JSON)
@Produces(APPLICATION_JSON)
class ExamineErrorExpressionResource {

    @POST
    fun examimeErrorExpression(request: ExamineErrorExpressionRequest) =
        FeelEngineWrapper.examineErrorExpression(request.context, request.errorExpression)
}

data class ExamineErrorExpressionRequest(val context: Any, val errorExpression: String)
