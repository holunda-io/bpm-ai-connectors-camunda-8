package io.holunda.feel.rest

import io.holunda.feel.core.*
import jakarta.ws.rs.*
import jakarta.ws.rs.core.MediaType
import jakarta.ws.rs.core.MediaType.*

@Path("/createOutputVariables")
@Consumes(APPLICATION_JSON)
@Produces(APPLICATION_JSON)
class CreateOutputVariablesResource {

    @POST
    fun createOutputVariables(request: CreateOutputVariablesRequest) =
        FeelEngineWrapper.createOutputVariables(request.context, request.resultExpression)
}

data class CreateOutputVariablesRequest(val context: Any, val resultExpression: String)
