package io.holunda.feel.rest;

import io.holunda.feel.core.ConnectorHelper;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Path("/createOutputVariables")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class CreateOutputVariablesResource {

    @POST
    public Object createOutputVariables(CreateOutputVariablesRequest request) {
        return ConnectorHelper.createOutputVariables(request.context(), request.resultExpression());
    }
}