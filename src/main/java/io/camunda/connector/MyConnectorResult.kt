package io.camunda.connector

import java.util.*

class MyConnectorResult {
    // TODO: define connector result properties, which are returned to the process engine
    var myProperty: String? = null
    override fun equals(o: Any?): Boolean {
        if (this === o) {
            return true
        }
        if (o == null || javaClass != o.javaClass) {
            return false
        }
        val that = o as MyConnectorResult
        return myProperty == that.myProperty
    }

    override fun hashCode(): Int {
        return Objects.hash(myProperty)
    }

    override fun toString(): String {
        return "MyConnectorResult [myProperty=$myProperty]"
    }
}
